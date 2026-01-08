import pytest
from parser.lexer import Lexer
from parser.parser import (
    Assign,
    Exit,
    Function,
    BinOp,
    Block,
    Compound,
    NoOp,
    Num,
    Param,
    Parser,
    Procedure,
    ProcedureCall,
    Program,
    Type,
    Var,
    VarDecl,
)
from parser.token import Token


data = [
    [
        "PROGRAM name;{ name } PROCEDURE proc; BEGIN b:=3 END; BEGIN\na:=proc() END.",
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
                        (),
                    ),
                ),
                Compound(
                    (
                        Assign(
                            Var(Token.Id("a")),
                            Token.assign(),
                            ProcedureCall("proc", (), Token.Id("proc")),
                        ),
                    )
                ),
            ),
        ),
    ],
    [
        "PROGRAM name; PROCEDURE proc(a, b: integer; c: real); BEGIN b:=3 END; BEGIN\na:=5 END.",
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
                        (
                            Param(Var(Token.Id("a")), Type(Token.integer())),
                            Param(Var(Token.Id("b")), Type(Token.integer())),
                            Param(Var(Token.Id("c")), Type(Token.real())),
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
    [
        "PROGRAM name; BEGIN ProcCall(a, 1+2); END.",
        Program(
            "name",
            Block(
                (),
                Compound(
                    (
                        ProcedureCall(
                            "ProcCall",
                            (
                                Var(Token.Id("a")),
                                BinOp(
                                    Num(Token.const_int("1")),
                                    Token.plus(),
                                    Num(Token.const_int("2")),
                                ),
                            ),
                            Token.Id("ProcCall"),
                        ),
                        NoOp(),
                    )
                ),
            ),
        ),
    ],
    ["PROGRAM empty; BEGIN end.", Program("empty", Block((), Compound((NoOp(),))))],
    [
        "PROGRAM nums; VAR a, b: INTEGER; BEGIN a:=5; exit; b:=a; END.",
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
                        Exit(),
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


decls_data = [
    [
        "PROCEDURE func1(a: integer); begin end;",
        (
            Procedure(
                "func1",
                Block((), Compound((NoOp(),))),
                (Param(Var(Token.Id("a")), Type(Token.integer())),),
            ),
        ),
    ],
    [
        "FUNCTION func1(a: integer): real; begin end;",
        (
            Function(
                "func1",
                Block((), Compound((NoOp(),))),
                (Param(Var(Token.Id("a")), Type(Token.integer())),),
                Type(Token.real()),
            ),
        ),
    ],
    [
        "VAR a, b :integer; VAR c: real;",
        (
            VarDecl(Var(Token.Id("a")), Type(Token.integer())),
            VarDecl(Var(Token.Id("b")), Type(Token.integer())),
            VarDecl(Var(Token.Id("c")), Type(Token.real())),
        ),
    ],
]


@pytest.mark.parametrize(("code", "result"), decls_data)
def test_declaractions(code, result):
    code = f"PROGRAM name; {code} BEGIN END."
    lexer = Lexer(code)
    parser = Parser(lexer)
    res = parser.parse()
    exp_result = Program("name", Block(result, Compound((NoOp(),))))
    assert res == exp_result
