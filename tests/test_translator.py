from src.lexer import Lexer
from src.parser import Parser
from src.translator import LISP, RPN


def test_rpn():
    lexer = Lexer("(5 + 3) * 12 / 3")
    parser = Parser(lexer)
    tranlator = RPN(parser)
    assert tranlator.process() == "5 3 + 12 * 3 /"


def test_lisp():
    lexer = Lexer("2 + 3 * 5")
    parser = Parser(lexer)
    tranlator = LISP(parser)
    assert tranlator.process() == "(+ 2 (* 3 5))"
