import logging
from pathlib import Path
import sys

from interpreter.interpreter import Interpreter
from interpreter.semantic_analyzer import SymbolTableVisitor
from parser.lexer import Lexer
from parser import Parser


def main() -> None:
    assert len(sys.argv) >= 2, "no file name provided"
    file = Path(sys.argv[1])
    assert file.is_file(), f"file {file} does not exist"
    with file.open() as f:
        code = f.read()
    semantic_logger = logging.Logger("semantic_logger")
    semantic_logger.setLevel(logging.DEBUG)
    interpreter_logger = logging.Logger("interpreter_logger")
    interpreter_logger.setLevel(logging.DEBUG)
    lexer = Lexer(code)
    parser = Parser(lexer)
    semantic_analyzer = SymbolTableVisitor.new(semantic_logger)
    interpreter = Interpreter(interpreter_logger)
    tree = parser.parse()
    interpreter.interpret(semantic_analyzer.analyze(tree))
