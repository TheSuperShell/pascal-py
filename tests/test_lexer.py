import pytest
from src.lexer import Lexer
from src.token import Token

data = [
    [
        "a := 10 + 9 - (2 / (4)) * 123;",
        [
            Token.Id("a"),
            Token.assign(),
            Token.integer("10"),
            Token.plus(),
            Token.integer("9"),
            Token.minus(),
            Token.open_p(),
            Token.integer("2"),
            Token.div(),
            Token.open_p(),
            Token.integer("4"),
            Token.close_p(),
            Token.close_p(),
            Token.mult(),
            Token.integer("123"),
            Token.semi(),
            Token.eof(),
        ],
    ],
    [
        "BEGIN\n\ta:=10;END.",
        [
            Token.begin(),
            Token.Id("a"),
            Token.assign(),
            Token.integer("10"),
            Token.semi(),
            Token.end(),
            Token.dot(),
            Token.eof(),
        ],
    ],
]


@pytest.mark.parametrize(("code", "result"), data)
def test_lexer_math(code, result):
    lexer = Lexer(code)
    assert list(lexer) == result


def test_remove_spaces():
    lexer_space = Lexer("10   +\t20/\n30")
    lexer = Lexer("10+20/30")
    assert list(lexer) == list(lexer_space)
