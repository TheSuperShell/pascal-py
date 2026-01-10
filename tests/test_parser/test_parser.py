import pytest
from parser.lexer import Lexer
from parser.parser import (
    Assign,
    Condition,
    Exit,
    ForStatement,
    Function,
    BinOp,
    Block,
    Compound,
    IfStatement,
    Literal,
    NoOp,
    Param,
    Parser,
    Procedure,
    Call,
    Program,
    Type,
    UnaryOp,
    Var,
    VarDecl,
    WhileStatement,
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
                                        Literal[int, None](Token.const_int("3"), int),
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
                            Call("proc", (), Token.Id("proc")),
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
                                        Literal[int, None](Token.const_int("3"), int),
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
                            Literal[int, None](Token.const_int("5"), int),
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
                        Call(
                            "ProcCall",
                            (
                                Var(Token.Id("a")),
                                BinOp(
                                    Literal[int, None](Token.const_int("1"), int),
                                    Token.plus(),
                                    Literal[int, None](Token.const_int("2"), int),
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
                            Literal[int, None](Token.const_int("5"), int),
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
        "PROGRAM fl; VAR val : REAL; BEGIN val:=FALSE OR 5 + (10 / 3) > NOT 10 + 0; x := True; some_text := 'hello \\'mom\\''; END.",
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
                                Literal[bool, None](
                                    Token.const_bool(False),
                                    lambda x: x.lower() == "true",
                                ),
                                Token.Or(),
                                BinOp(
                                    BinOp(
                                        Literal[int, None](Token.const_int("5"), int),
                                        Token.plus(),
                                        BinOp(
                                            Literal[int, None](
                                                Token.const_int("10"), int
                                            ),
                                            Token.float_div(),
                                            Literal[int, None](
                                                Token.const_int("3"), int
                                            ),
                                        ),
                                    ),
                                    Token.gt(),
                                    UnaryOp(
                                        Token.Not(),
                                        BinOp(
                                            Literal[int, None](
                                                Token.const_int("10"), int
                                            ),
                                            Token.plus(),
                                            Literal[int, None](
                                                Token.const_int("0"), int
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        Assign(
                            Var(Token.Id("x")),
                            Token.assign(),
                            Literal[bool, None](
                                Token.const_bool(True), lambda x: x.lower() == "true"
                            ),
                        ),
                        Assign(
                            Var(Token.Id("some_text")),
                            Token.assign(),
                            Literal[str, None](
                                Token.const_string("hello 'mom'"), lambda x: x
                            ),
                        ),
                        NoOp(),
                    )
                ),
            ),
        ),
    ],
    [
        "PROGRAM if_st; BEGIN IF (TRUE) THEN x:=10 ELSE IF (10 > 3) THEN BEGIN a := 10 END ELSE b := False; END.",
        Program(
            "if_st",
            Block(
                (),
                Compound(
                    (
                        IfStatement(
                            Condition(
                                Literal[bool, None](
                                    Token.const_bool(True),
                                    lambda x: x.lower() == "true",
                                ),
                                Assign(
                                    Var(Token.Id("x")),
                                    Token.assign(),
                                    Literal[int, None](Token.const_int("10"), int),
                                ),
                            ),
                            (
                                Condition(
                                    BinOp(
                                        Literal[int, None](Token.const_int("10"), int),
                                        Token.gt(),
                                        Literal[int, None](Token.const_int("3"), int),
                                    ),
                                    Compound(
                                        (
                                            Assign(
                                                Var(Token.Id("a")),
                                                Token.assign(),
                                                Literal[int, None](
                                                    Token.const_int("10"), int
                                                ),
                                            ),
                                        )
                                    ),
                                ),
                            ),
                            Assign(
                                Var(Token.Id("b")),
                                Token.assign(),
                                Literal[bool, None](
                                    Token.const_bool(False), lambda x: bool(x)
                                ),
                            ),
                        ),
                        NoOp(),
                    )
                ),
            ),
        ),
    ],
    [
        "PROGRAM while_st; BEGIN WHILE (True) DO x := 10; FOR x := 0 to 10 do y := 0 END.",
        Program(
            "while_st",
            Block(
                (),
                Compound(
                    (
                        WhileStatement(
                            Literal[bool, None](Token.const_bool(True), bool),
                            Assign(
                                Var(Token.Id("x")),
                                Token.assign(),
                                Literal[int, None](Token.const_int("10"), int),
                            ),
                        ),
                        ForStatement(
                            Var(Token.Id("x")),
                            Literal[int, None](Token.const_int("0"), int),
                            Literal[int, None](Token.const_int("10"), int),
                            Assign(
                                Var(Token.Id("y")),
                                Token.assign(),
                                Literal[int, None](Token.const_int("0"), int),
                            ),
                        ),
                    )
                ),
            ),
        ),
    ],
]


@pytest.mark.parametrize(("code", "result"), data)
def test_parser(code, result):
    lexer = Lexer(code)
    parser = Parser[None](lexer)
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
        "VAR a, b :integer; VAR c: real; VAR x : BOOLEAN; VAR text : STRING; var character: char;",
        (
            VarDecl(Var(Token.Id("a")), Type(Token.integer())),
            VarDecl(Var(Token.Id("b")), Type(Token.integer())),
            VarDecl(Var(Token.Id("c")), Type(Token.real())),
            VarDecl(Var(Token.Id("x")), Type(Token.boolean())),
            VarDecl(Var(Token.Id("text")), Type(Token.string())),
            VarDecl(Var(Token.Id("character")), Type(Token.char())),
        ),
    ],
]


@pytest.mark.parametrize(("code", "result"), decls_data)
def test_declaractions(code, result):
    code = f"PROGRAM name; {code} BEGIN END."
    lexer = Lexer(code)
    parser = Parser[None](lexer)
    res = parser.parse()
    exp_result = Program("name", Block(result, Compound((NoOp(),))))
    assert res == exp_result
