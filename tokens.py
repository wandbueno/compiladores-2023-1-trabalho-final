from enum import Enum
from dataclasses import dataclass


class TokenClass(Enum):
    PONTO_FLUTUANTE = r"\d+\.\d+"
    CONSTANTE_INTEIRA = r"\b\d+\b"
    PALAVRA_RESERVADA = r"\b(struct|if|int|else|while|do|for|float|double|char|long|short|break|continue|case|switch|default|void|return|print|nil|fun|var)\b"
    OPERADOR = r"(<|>|=|==|!=|<=|>=|\|\||&&|\+=|-=|\*=|-=|--|\+\+|\+|\/|->|\*|-|\||!|&|%|and|or)"
    DELIMITADOR = r"[\[\](){};,]"
    CONSTANTE_TEXTO = r'"[^"]*"'
    IDENTIFICADOR = r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"


token_index = 0
previous_token = None


@dataclass
class Token:
    token_class: TokenClass
    lexeme: str
    line: int
    column: int

    def __str__(self):
        return f'<{self.token_class.name}> {self.lexeme}'
