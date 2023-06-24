import os
import re
from analyzer import parse_code, program


def main():
    try:
        with open('teste/teste4.c', 'r', encoding='utf-8') as f:
            code = f.read()

        code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        code = re.sub(r'//\s*[^\n]*', '', code, flags=re.DOTALL)

        tokens = parse_code(code)

        output_file = "output.py"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(program())

        print("\nAnálise sintática concluída com sucesso!!!")

        print(
            f"\nTradução para Python concluída com sucesso!!!. Arquivo de saída gerado: {output_file}")

    except SyntaxError as e:
        print(f"{e}")
        return 1

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
