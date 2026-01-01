from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser


def main():
    while True:
        try:
            inp = input("enter expression: ")
        except KeyboardInterrupt:
            break
        lexer = Lexer(inp)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        print(f"Operation result: {interpreter.interpret()}")


if __name__ == "__main__":
    main()
