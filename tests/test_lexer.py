import pytest
from src.lexer import Lexer
from src.token import Token

data = [
    [
        "a := 10 + 9 / 4.3 - (2 div (4)) * 123;",
        [
            Token.Id("a"),
            Token.assign(),
            Token.const_int("10"),
            Token.plus(),
            Token.const_int("9"),
            Token.float_div(),
            Token.const_float("4.3"),
            Token.minus(),
            Token.open_p(),
            Token.const_int("2"),
            Token.int_div(),
            Token.open_p(),
            Token.const_int("4"),
            Token.close_p(),
            Token.close_p(),
            Token.mult(),
            Token.const_int("123"),
            Token.semi(),
            Token.eof(),
        ],
    ],
    [
        "BEGIN\n\t_a_4:=10;end.",
        [
            Token.begin(),
            Token.Id("_a_4"),
            Token.assign(),
            Token.const_int("10"),
            Token.semi(),
            Token.end(),
            Token.dot(),
            Token.eof(),
        ],
    ],
    [
        "PROGRAM\n PROCEDURE VAR:\nA, B:INTEGER { other } BEGIN { some comment }\n{other}; END.",
        [
            Token.program(),
            Token.procedure(),
            Token.var(),
            Token.colon(),
            Token.Id("A"),
            Token.comma(),
            Token.Id("B"),
            Token.colon(),
            Token.integer(),
            Token.begin(),
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
    lexer_space = Lexer("10   +\t20-\n30")
    lexer = Lexer("10+20-30")
    assert list(lexer) == list(lexer_space)
