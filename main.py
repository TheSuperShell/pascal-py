from src.interpreter import Interpreter
from src.lexer import Lexer


def main():
    while True:
        try:
            inp = input("enter expression: ")
        except KeyboardInterrupt:
            break
        lexer = Lexer(inp)
        # for t in lexer:
        #     print(t)
        interpreter = Interpreter(lexer)
        print(f"Operation result: {interpreter.expr()}")


if __name__ == "__main__":
    main()
