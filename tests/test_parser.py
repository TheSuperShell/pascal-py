from hypothesis import given, strategies as st
from src.lexer import Lexer
from src.parser import Num, Parser, BinOp
from src.token import Token


def test_parser_math():
    lexer = Lexer("1 + 2 / 3 - 4")
    parser = Parser(lexer)
    expected = BinOp(
        BinOp(
            Num(Token.integer("1")),
            Token.plus(),
            BinOp(
                Num(Token.integer("2")),
                Token.div(),
                Num(Token.integer("3")),
            ),
        ),
        Token.minus(),
        Num(Token.integer("4")),
    )
    res = parser.parse()
    assert res == expected


OPS = ["+", "-", "*", "/"]


@given(
    st.lists(
        st.tuples(
            st.integers(min_value=1),
            st.integers(min_value=0, max_value=3),
        ),
        min_size=1,
    )
)
def test_intepreter_math(int_op: list[tuple[int, int]]):
    inp = []
    inp.append(str(int_op[0][0]))
    for i in range(0, len(int_op) - 1):
        inp.append(OPS[int_op[i][1]])
        inp.append(str(int_op[i + 1][0]))
    code = "".join(inp)
    lexer = Lexer(code)
    parser = Parser(lexer)
    result = parser.parse()
    assert str(result) == code
