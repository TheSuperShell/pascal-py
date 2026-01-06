from pathlib import Path
import sys
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser


def main():
    assert len(sys.argv) >= 2, "no file name provided"
    file = Path(sys.argv[1])
    assert file.is_file(), f"file {file} does not exist"
    with file.open() as f:
        code = f.read()
    lexer = Lexer(code)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.process()


if __name__ == "__main__":
    main()
