import pytest
from parser.lexer import Lexer
from parser.parser import (
    Assign,
    Bool,
    Condition,
    Exit,
    ForStatement,
    Function,
    BinOp,
    Block,
    Compound,
    IfStatement,
    NoOp,
    Num,
    Param,
    Parser,
    Procedure,
    Call,
    Program,
    Str,
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
                        Call(
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
                                Bool(Token.const_bool(False)),
                                Token.Or(),
                                BinOp(
                                    BinOp(
                                        Num(Token.const_int("5")),
                                        Token.plus(),
                                        BinOp(
                                            Num(Token.const_int("10")),
                                            Token.float_div(),
                                            Num(Token.const_int("3")),
                                        ),
                                    ),
                                    Token.gt(),
                                    UnaryOp(
                                        Token.Not(),
                                        BinOp(
                                            Num(Token.const_int("10")),
                                            Token.plus(),
                                            Num(Token.const_int("0")),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        Assign(
                            Var(Token.Id("x")),
                            Token.assign(),
                            Bool(Token.const_bool(True)),
                        ),
                        Assign(
                            Var(Token.Id("some_text")),
                            Token.assign(),
                            Str(Token.const_string("hello 'mom'")),
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
                                Bool(Token.const_bool(True)),
                                Assign(
                                    Var(Token.Id("x")),
                                    Token.assign(),
                                    Num(Token.const_int("10")),
                                ),
                            ),
                            (
                                Condition(
                                    BinOp(
                                        Num(Token.const_int("10")),
                                        Token.gt(),
                                        Num(Token.const_int("3")),
                                    ),
                                    Compound(
                                        (
                                            Assign(
                                                Var(Token.Id("a")),
                                                Token.assign(),
                                                Num(Token.const_int("10")),
                                            ),
                                        )
                                    ),
                                ),
                            ),
                            Assign(
                                Var(Token.Id("b")),
                                Token.assign(),
                                Bool(Token.const_bool(False)),
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
                            Bool(Token.const_bool(True)),
                            Assign(
                                Var(Token.Id("x")),
                                Token.assign(),
                                Num(Token.const_int("10")),
                            ),
                        ),
                        ForStatement(
                            Var(Token.Id("x")),
                            Num(Token.const_int("0")),
                            Num(Token.const_int("10")),
                            Assign(
                                Var(Token.Id("y")),
                                Token.assign(),
                                Num(Token.const_int("0")),
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
    parser = Parser(lexer)
    res = parser.parse()
    exp_result = Program("name", Block(result, Compound((NoOp(),))))
    assert res == exp_result
