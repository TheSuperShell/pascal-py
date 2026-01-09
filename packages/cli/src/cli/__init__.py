import argparse
from dataclasses import dataclass
import logging
from pathlib import Path
import sys

from interpreter.interpreter import Interpreter
from interpreter.semantic_analyzer import SymbolTableVisitor
from parser.lexer import Lexer
from parser import Parser


def configure_loggers(
    log_scope: bool, log_stack: bool
) -> tuple[logging.Logger, logging.Logger]:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    semantic_logger = logging.Logger("semantic_logger")
    semantic_logger.setLevel(logging.DEBUG if log_scope else logging.WARNING)
    semantic_logger.addHandler(stdout_handler)
    interpreter_logger = logging.Logger("interpreter_logger")
    interpreter_logger.setLevel(logging.DEBUG if log_stack else logging.WARNING)
    interpreter_logger.addHandler(stdout_handler)
    return semantic_logger, interpreter_logger


@dataclass(slots=True, frozen=True)
class Input:
    file: Path
    log_stack: bool
    log_scope: bool


def parse_input() -> Input:
    parser = argparse.ArgumentParser(description="Interpret a pascal file")
    parser.add_argument("inputfile", help="Pascal source file")
    parser.add_argument("--scope", help="DEBUG mode for scope", action="store_true")
    parser.add_argument("--stack", help="DEBUG mode for stack", action="store_true")
    args = parser.parse_args()
    return Input(Path(args.inputfile), args.stack, args.scope)


def main() -> None:
    inp = parse_input()
    assert inp.file.is_file(), f"file {inp.file} does not exist"
    with inp.file.open() as f:
        code = f.read()
    lexer = Lexer(code)
    parser = Parser(lexer)
    semantic_logger, interpreter_logger = configure_loggers(
        inp.log_scope, inp.log_stack
    )
    semantic_analyzer = SymbolTableVisitor.new(semantic_logger)
    interpreter = Interpreter(interpreter_logger)
    tree = parser.parse()
    interpreter.interpret(semantic_analyzer.analyze(tree))
