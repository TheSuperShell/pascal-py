from pathlib import Path
import sys
from src.interpreter import DefaultVisitor, Interpreter
from src.lexer import Lexer
from src.parser import Parser
from src.semantic_analyzer import SymbolTableVisitor


def main():
    assert len(sys.argv) >= 2, "no file name provided"
    file = Path(sys.argv[1])
    assert file.is_file(), f"file {file} does not exist"
    with file.open() as f:
        code = f.read()
    lexer = Lexer(code)
    parser = Parser(lexer)
    symbols = SymbolTableVisitor()
    default_visitor = DefaultVisitor()
    interpreter = Interpreter(parser, symbols, default_visitor)
    interpreter.process()
    for k, v in default_visitor.global_scope.items():
        print(f"{k} = {v}")


if __name__ == "__main__":
    main()
