from hypothesis import given, strategies as st
import pytest
from src.lexer import Lexer
from src.parser import Assign, BinOp, Compund, NoOp, Num, Parser, Var
from src.token import Token


data = [
    [
        "BEGIN\na:=5 END.",
        Compund((Assign(Var(Token.Id("a")), Token.assign(), Num(Token.integer("5"))),)),
    ],
    ["BEGIN END.", Compund((NoOp(),))],
    [
        "BEGIN a:=5; b:=a; END.",
        Compund(
            (
                Assign(Var(Token.Id("a")), Token.assign(), Num(Token.integer("5"))),
                Assign(Var(Token.Id("b")), Token.assign(), Var(Token.Id("a"))),
                NoOp(),
            )
        ),
    ],
    [
        "BEGIN val:=5 + (10 / 3); END.",
        Compund(
            (
                Assign(
                    Var(Token.Id("val")),
                    Token.assign(),
                    BinOp(
                        Num(Token.integer("5")),
                        Token.plus(),
                        BinOp(
                            Num(Token.integer("10")),
                            Token.div(),
                            Num(Token.integer("3")),
                        ),
                    ),
                ),
                NoOp(),
            )
        ),
    ],
]


@pytest.mark.parametrize(("code", "result"), data)
def test_parser(code, result):
    lexer = Lexer("BEGIN\na:=5 END.")
    parser = Parser(lexer)
    expected = Compund(
        (Assign(Var(Token.Id("a")), Token.assign(), Num(Token.integer("5"))),)
    )
    res = parser.parse()
    assert res == expected


OPS = ["+", "-", "*", "/"]


@given(
    st.lists(
        st.tuples(
            st.integers(),
            st.integers(min_value=0, max_value=3),
        ),
        min_size=1,
    )
)
def test_parser_rand_math(int_op: list[tuple[int, int]]):
    inp = ["BEGIN\nval:="]
    inp.append(str(int_op[0][0]))
    for i in range(0, len(int_op) - 1):
        inp.append(OPS[int_op[i][1]])
        inp.append(str(int_op[i + 1][0]))
    inp.append("\nEND.")
    code = "".join(inp)
    lexer = Lexer(code)
    parser = Parser(lexer)
    result = parser.parse()
    assert str(result) == code[:-1]
