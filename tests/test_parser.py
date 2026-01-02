import pytest
from src.lexer import Lexer
from src.parser import (
    Assign,
    BinOp,
    Block,
    Compound,
    NoOp,
    Num,
    Parser,
    Procedure,
    Program,
    Type,
    Var,
    VarDecl,
)
from src.token import Token


data = [
    [
        "PROGRAM name;{ name } PROCEDURE proc; BEGIN b:=3 END; BEGIN\na:=5 END.",
        Program(
            "name",
            Block(
                (
                    Procedure(
                        "proc",
                        Block(
                            (),
                            Compound(
                                (
                                    Assign(
                                        Var(
                                            Token.Id("b"),
                                        ),
                                        Token.assign(),
                                        Num(Token.const_int("3")),
                                    ),
                                )
                            ),
                        ),
                    ),
                ),
                Compound(
                    (
                        Assign(
                            Var(Token.Id("a")),
                            Token.assign(),
                            Num(Token.const_int("5")),
                        ),
                    )
                ),
            ),
        ),
    ],
    ["PROGRAM empty; BEGIN end.", Program("empty", Block((), Compound((NoOp(),))))],
    [
        "PROGRAM nums; VAR a, b: INTEGER; BEGIN a:=5; b:=a; END.",
        Program(
            "nums",
            Block(
                (
                    VarDecl(Var(Token.Id("a")), Type(Token.integer())),
                    VarDecl(Var(Token.Id("b")), Type(Token.integer())),
                ),
                Compound(
                    (
                        Assign(
                            Var(Token.Id("a")),
                            Token.assign(),
                            Num(Token.const_int("5")),
                        ),
                        Assign(Var(Token.Id("b")), Token.assign(), Var(Token.Id("a"))),
                        NoOp(),
                    )
                ),
            ),
        ),
    ],
    [
        "PROGRAM fl; VAR val : REAL; BEGIN val:=5 + (10 / 3); END.",
        Program(
            "fl",
            Block(
                (VarDecl(Var(Token.Id("val")), Type(Token.real())),),
                Compound(
                    (
                        Assign(
                            Var(Token.Id("val")),
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
