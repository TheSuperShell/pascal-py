import pytest
from hypothesis import given, strategies as st
from parser.lexer import _RESERVED_KEYWORDS, Lexer
from parser.token import Token

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
    [
        "> >= < <= <> =",
        [
            Token.gt(),
            Token.get(),
            Token.lt(),
            Token.let(),
            Token.neq(),
            Token.eq(),
            Token.eof(),
        ],
    ],
    [
        "'some text' 'a' 'some number=10.3' 'screening \\'example\\''",
        [
            Token.const_string("some text"),
            Token.const_char("a"),
            Token.const_string("some number=10.3"),
            Token.const_string("screening 'example'"),
            Token.eof(),
        ],
    ],
]


@pytest.mark.parametrize(("code", "result"), data)
def test_lexer_math(code, result):
    lexer = Lexer(code)
    assert list(lexer) == result


@given(
    st.lists(
        st.integers(min_value=0, max_value=len(_RESERVED_KEYWORDS) - 1), min_size=1
    )
)
def test_keywords(ls):
    res_keywords = list(_RESERVED_KEYWORDS)
    key_words = [res_keywords[i] for i in ls]
    result = [_RESERVED_KEYWORDS[key] for key in key_words] + [Token.eof()]
    lexer = Lexer(" ".join(key_words))
    assert result == list(lexer)


def test_remove_spaces():
    lexer_space = Lexer("10   +\t20-\n30")
    lexer = Lexer("10+20-30")
    assert list(lexer) == list(lexer_space)
