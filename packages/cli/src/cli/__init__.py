from pathlib import Path
import sys

from interpreter.interpreter import Interpreter
from parser.lexer import Lexer
from parser import Parser


def main() -> None:
    assert len(sys.argv) >= 2, "no file name provided"
    file = Path(sys.argv[1])
    assert file.is_file(), f"file {file} does not exist"
    with file.open() as f:
        code = f.read()
    lexer = Lexer(code)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.process()
