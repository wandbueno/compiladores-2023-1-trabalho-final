import re
import sys
from enum import Enum
from dataclasses import dataclass
from tokens import *


def parse_code(code):
    global tokens
    lines = code.split('\n')
    tokens = []
    line_num = 1

    for line in lines:
        line = re.sub(r'\s+', ' ', line.strip())
        column = 1

        while line:
            match = None
            for token_class in TokenClass:
                regex = token_class.value
                match = re.match(regex, line)
                if match:
                    lexeme = match.group(0)
                    token = Token(token_class, lexeme, line_num, column)
                    tokens.append(token)
                    line = line[len(lexeme):].lstrip()
                    column += len(lexeme)
                    break

            if match is None:
                raise SyntaxError(
                    f"Erro léxico na linha {line_num}, coluna {column}: caractere inesperado: {line[0]!r}")

        line_num += 1

    return tokens


def program():
    global token_index, tokens
    token_index = 0
    python_code = ""
    while not end_of_file():
        python_code += declaration() + "\n"
    if not end_of_file():
        error("Unexpected token", tokens[token_index])
    return python_code


def declaration():
    if check(TokenClass.PALAVRA_RESERVADA, "fun"):
        return funDecl()
    elif check(TokenClass.PALAVRA_RESERVADA, "var"):
        return varDecl()
    else:
        return statement()


def funDecl():
    match(TokenClass.PALAVRA_RESERVADA, "fun")
    identifier = tokens[token_index].lexeme
    match(TokenClass.IDENTIFICADOR)
    match(TokenClass.DELIMITADOR, "(")
    parameters_str = ""
    if check(TokenClass.IDENTIFICADOR):
        parameters_str = parameters()
    match(TokenClass.DELIMITADOR, ")")
    python_code = f"def {identifier}{parameters_str}:"
    block_code = block()
    indentation_block = '\n'.join(
        ['\t' + line for line in block_code.split('\n')])
    python_code += f"\n{indentation_block}"

    return python_code


def varDecl():
    match(TokenClass.PALAVRA_RESERVADA, "var")
    identifier = tokens[token_index].lexeme
    match(TokenClass.IDENTIFICADOR)
    python_code = f"{identifier}"
    if check(TokenClass.OPERADOR, "="):
        match(TokenClass.OPERADOR, "=")
        content = expression()
        python_code += f" = {content}"
    match(TokenClass.DELIMITADOR, ";")
    return python_code


def statement():
    if check(TokenClass.PALAVRA_RESERVADA, "print"):
        return printStmt()
    elif check(TokenClass.PALAVRA_RESERVADA, "if"):
        return ifStmt()
    elif check(TokenClass.PALAVRA_RESERVADA, "for"):
        return forStmt()
    elif check(TokenClass.PALAVRA_RESERVADA, "return"):
        return returnStmt()
    elif check(TokenClass.PALAVRA_RESERVADA, "while"):
        return whileStmt()
    elif check(TokenClass.DELIMITADOR, "{"):
        return block()
    else:
        return exprStmt()


def ifStmt():
    match(TokenClass.PALAVRA_RESERVADA, "if")
    match(TokenClass.DELIMITADOR, "(")
    condition = expression()
    match(TokenClass.DELIMITADOR, ")")
    then_statement = statement()

    indentation_if = '\n'.join(
        ['\t' + line for line in then_statement.split('\n')])
    python_code = f"if {condition}:\n{indentation_if}"

    while check(TokenClass.PALAVRA_RESERVADA, "else") and not check(TokenClass.PALAVRA_RESERVADA, "if"):
        match(TokenClass.PALAVRA_RESERVADA, "else")

        if check(TokenClass.PALAVRA_RESERVADA, "if"):
            match(TokenClass.PALAVRA_RESERVADA, "if")
            elif_condition = expression()
            elif_statement = statement()
            indentation_elif = '\n'.join(
                ['\t' + line for line in elif_statement.split('\n')])

            python_code += f"\nelif {elif_condition}:\n{indentation_elif}"
        else:
            else_statement = statement()
            indentation_else = '\n'.join(
                ['\t' + line for line in else_statement.split('\n')])
            python_code += f"\nelse:\n{indentation_else}"

    return python_code


def printStmt():
    match(TokenClass.PALAVRA_RESERVADA, "print")
    content = expression()
    match(TokenClass.DELIMITADOR, ";")
    python_code = f"print({content})"
    return python_code


def returnStmt():
    match(TokenClass.PALAVRA_RESERVADA, "return")
    if not check(TokenClass.DELIMITADOR, ";"):
        return_value = expression()
    match(TokenClass.DELIMITADOR, ";")

    python_code = f"return {return_value}"
    return python_code


def forStmt():
    match(TokenClass.PALAVRA_RESERVADA, "for")
    match(TokenClass.DELIMITADOR, "(")

    if check(TokenClass.PALAVRA_RESERVADA, "var"):
        varDecl()
    elif not check(TokenClass.DELIMITADOR, ";"):
        exprStmt()

    match(TokenClass.DELIMITADOR, ";")

    if not check(TokenClass.DELIMITADOR, ";"):
        expression()

    match(TokenClass.DELIMITADOR, ";")

    if not check(TokenClass.DELIMITADOR, ")"):
        expression()

    match(TokenClass.DELIMITADOR, ")")

    statement()

    python_code = "for "
    if check(TokenClass.PALAVRA_RESERVADA, "var"):
        python_code += varDecl()
    else:
        python_code += exprStmt()

    python_code += "; " + expression()
    python_code += "; " + expression()
    python_code += ":"

    return python_code


def whileStmt():
    match(TokenClass.PALAVRA_RESERVADA, "while")
    match(TokenClass.DELIMITADOR, "(")

    condition = expression()

    match(TokenClass.DELIMITADOR, ")")

    body = statement()

    python_code = f"while {condition}:"
    python_code += f"\n\t{body}"
    # indentation_block = '\n'.join(['\t' + line for line in body.split('\n')])
    # python_code += f"\n{indentation_block}"

    return python_code


def block():
    match(TokenClass.DELIMITADOR, "{")
    python_code = ""
    while not check(TokenClass.DELIMITADOR, "}") and not end_of_file():
        python_code += declaration() + "\n"
    match(TokenClass.DELIMITADOR, "}")
    return python_code


def exprStmt():
    content = expression()
    match(TokenClass.DELIMITADOR, ";")
    python_code = f"{content}"
    return python_code


def expression():
    return assignment()


def assignment():
    if check(TokenClass.IDENTIFICADOR):
        identifier = tokens[token_index].lexeme
        match(TokenClass.IDENTIFICADOR)
        if check(TokenClass.OPERADOR, "="):
            match(TokenClass.OPERADOR, "=")
            content = assignment()
            python_code = f"{identifier} = {content}"
            return python_code
        else:
            prev_token()
            return logic_or()
    else:
        return logic_or()


def logic_or():
    python_code = logic_and()
    while check(TokenClass.OPERADOR, "or"):
        match(TokenClass.OPERADOR, "or")
        right_operand = logic_and()
        python_code = f"{python_code} or {right_operand}"
    return python_code


def logic_and():
    python_code = equality()
    while check(TokenClass.OPERADOR, "and"):
        match(TokenClass.OPERADOR, "and")
        right_operand = equality()
        python_code = f"{python_code} and {right_operand}"
    return python_code


def equality():
    python_code = comparison()
    while check(TokenClass.OPERADOR, ["!=", "=="]):
        operator = tokens[token_index].lexeme
        match(TokenClass.OPERADOR)
        right_operand = comparison()
        python_code = f"{python_code} {operator} {right_operand}"
    return python_code


def comparison():
    python_code = term()
    while check(TokenClass.OPERADOR) and tokens[token_index].lexeme in ["<", ">", "<=", ">="]:
        operator = tokens[token_index].lexeme
        match(TokenClass.OPERADOR)
        right_operand = term()
        python_code = f"{python_code} {operator} {right_operand}"
    return python_code


def term():
    python_code = factor()
    while True:
        if check(TokenClass.OPERADOR, "+"):
            operator = tokens[token_index].lexeme
            match(TokenClass.OPERADOR, "+")
            right_operand = factor()
            python_code = f"{python_code} {operator} {right_operand}"
        elif check(TokenClass.OPERADOR, "-"):
            operator = tokens[token_index].lexeme
            match(TokenClass.OPERADOR, "-")
            right_operand = factor()
            python_code = f"{python_code} {operator} {right_operand}"
        else:
            break
    return python_code


def factor():
    python_code = unary()
    while check(TokenClass.OPERADOR, "/") or check(TokenClass.OPERADOR, "*"):
        operator = tokens[token_index].lexeme
        match(TokenClass.OPERADOR)
        right_operand = unary()
        python_code = f"{python_code} {operator} {right_operand}"
    return python_code


def unary():
    if check(TokenClass.OPERADOR, "!") or check(TokenClass.OPERADOR, "-"):
        operator = tokens[token_index].lexeme
        match(TokenClass.OPERADOR)
        operand = unary()
        python_code = f"{operator} {operand}"
    else:
        python_code = call()
    return python_code


def call():
    python_code = primary()
    while check(TokenClass.DELIMITADOR, "(") or check(TokenClass.DELIMITADOR, "."):
        if check(TokenClass.DELIMITADOR, "("):
            match(TokenClass.DELIMITADOR, "(")
            python_code += "(" + arguments() + ")"
            match(TokenClass.DELIMITADOR, ")")
        elif check(TokenClass.DELIMITADOR, "."):
            match(TokenClass.DELIMITADOR, ".")
            identifier = tokens[token_index].lexeme
            match(TokenClass.IDENTIFICADOR)
            python_code += "." + identifier
    return python_code


def primary():
    if check(TokenClass.PALAVRA_RESERVADA, "true") or \
       check(TokenClass.PALAVRA_RESERVADA, "false") or \
       check(TokenClass.PALAVRA_RESERVADA, "nil") or \
       check(TokenClass.PALAVRA_RESERVADA, "this") or \
       check(TokenClass.CONSTANTE_INTEIRA) or \
       check(TokenClass.CONSTANTE_TEXTO) or \
       check(TokenClass.IDENTIFICADOR):
        token = next_token()
        if token.lexeme == "nil":
            return "None"
        else:
            return token.lexeme
    elif check(TokenClass.PALAVRA_RESERVADA, "super"):
        match(TokenClass.PALAVRA_RESERVADA, "super")
        match(TokenClass.DELIMITADOR, ".")
        identifier = tokens[token_index].lexeme
        match(TokenClass.IDENTIFICADOR)
        return "super." + identifier
    elif check(TokenClass.DELIMITADOR, "("):
        match(TokenClass.DELIMITADOR, "(")
        python_code = "(" + expression() + ")"
        match(TokenClass.DELIMITADOR, ")")
        return python_code
    else:
        token = None if end_of_file() else tokens[token_index]
        raise SyntaxError(
            f"\nToken inesperado na expressão primária: {token.token_class.name} {token.lexeme}, linha {token.line}, coluna {token.column}")


def function():
    identifier = tokens[token_index].lexeme
    match(TokenClass.IDENTIFICADOR)
    match(TokenClass.DELIMITADOR, '(')
    parameters_code = parameters()
    match(TokenClass.DELIMITADOR, ')')
    block_code = block()
    python_code = f"def {identifier}{parameters_code}:"
    python_code += f"\n{block_code}"
    return python_code


def parameters():
    identifier = tokens[token_index].lexeme
    match(TokenClass.IDENTIFICADOR)
    parameters_code = f"({identifier}"
    while check(TokenClass.DELIMITADOR, ","):
        match(TokenClass.DELIMITADOR, ",")
        identifier = tokens[token_index].lexeme
        match(TokenClass.IDENTIFICADOR)
        parameters_code += f", {identifier}"
    parameters_code += ")"
    return parameters_code


def arguments():
    argument_code = expression()
    while check(TokenClass.DELIMITADOR, ","):
        match(TokenClass.DELIMITADOR, ",")
        argument_code += ", " + expression()
    return argument_code


# FUNÇÕES AUXILIARES ***************************

def end_of_file():
    global tokens, token_index
    return token_index >= len(tokens)


def check(expected_class, expected_value=None):
    global tokens, token_index
    if not end_of_file():
        token = tokens[token_index]
        if token.token_class == expected_class and (expected_value is None or token.lexeme == expected_value):
            return True
    return False


def match(expected_token_class, expected_token_value=None, function_name=None):
    global previous_token
    if not check(expected_token_class, expected_token_value):
        token = None if end_of_file() else tokens[token_index]
        expected_value_str = expected_token_value if expected_token_value is not None else "None"
        found_token_class_str = token.token_class.name if token is not None else "None"
        found_lexeme_str = token.lexeme if token is not None else "None"
        function_name_str = f" na função {function_name}" if function_name is not None else ""
        error_message = f"\nErro de análise sintática: Esperado {expected_token_class.name} {expected_value_str}, encontrado {found_token_class_str} {found_lexeme_str}{function_name_str}"
        error(error_message, token)
    else:
        previous_token = tokens[token_index]
        next_token()


def next_token():
    global token_index, tokens

    if not end_of_file():
        token = tokens[token_index]
        print(f"Token atual: {token}")
        token_index += 1
        return token
    else:
        return None


def prev_token():
    global token_index, previous_token
    if token_index > 0:
        token_index -= 1
        previous_token = tokens[token_index]
        return tokens[token_index]


def error(message, token=None):
    if token:
        message += f", na linha {token.line}, coluna {token.column}"
    else:
        message += " no final do arquivo"
    raise SyntaxError(message)
