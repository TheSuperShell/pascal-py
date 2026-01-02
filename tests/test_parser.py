import pytest
from src.lexer import Lexer
from src.parser import (
    Assign,
    BinOp,
    Block,
    Compund,
    NoOp,
    Num,
    Parser,
    Program,
    Type,
    Var,
    VarDecl,
)
from src.token import Token


data = [
    [
        "PROGRAM name;{ name } BEGIN\na:=5 END.",
        Program(
            "NAME",
            Block(
                (),
                Compund(
                    (
                        Assign(
                            Var(Token.Id("A")),
                            Token.assign(),
                            Num(Token.const_int("5")),
                        ),
                    )
                ),
            ),
        ),
    ],
    ["PROGRAM empty; BEGIN END.", Program("EMPTY", Block((), Compund((NoOp(),))))],
    [
        "PROGRAM nums; VAR a, b: INTEGER; BEGIN a:=5; b:=a; END.",
        Program(
            "NUMS",
            Block(
                (
                    VarDecl(Var(Token.Id("A")), Type(Token.integer())),
                    VarDecl(Var(Token.Id("B")), Type(Token.integer())),
                ),
                Compund(
                    (
                        Assign(
                            Var(Token.Id("A")),
                            Token.assign(),
                            Num(Token.const_int("5")),
                        ),
                        Assign(Var(Token.Id("B")), Token.assign(), Var(Token.Id("A"))),
                        NoOp(),
                    )
                ),
            ),
        ),
    ],
    [
        "PROGRAM fl; VAR VAL : REAL; BEGIN val:=5 + (10 / 3); END.",
        Program(
            "FL",
            Block(
                (VarDecl(Var(Token.Id("VAL")), Type(Token.real())),),
                Compund(
                    (
                        Assign(
                            Var(Token.Id("VAL")),
                            Token.assign(),
                            BinOp(
                                Num(Token.const_int("5")),
                                Token.plus(),
                                BinOp(
                                    Num(Token.const_int("10")),
                                    Token.float_div(),
                                    Num(Token.const_int("3")),
                                ),
                            ),
                        ),
                        NoOp(),
                    )
                ),
            ),
        ),
    ],
]


@pytest.mark.parametrize(("code", "result"), data)
def test_parser(code, result):
    lexer = Lexer(code)
    parser = Parser(lexer)
    res = parser.parse()
    assert res == result
