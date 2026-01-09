from dataclasses import dataclass
from enum import IntEnum, auto


class TokenType(IntEnum):
    PROGRAM = auto()
    INTEGER = auto()
    REAL = auto()
    BOOLEAN = auto()
    CHAR = auto()
    STRING = auto()
    INTEGER_CONST = auto()
    REAL_CONST = auto()
    BOOLEAN_CONST = auto()
    CHAR_CONST = auto()
    STRING_CONST = auto()
    COMMA = auto()
    COLON = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLICATION = auto()
    INTEGER_DIV = auto()
    FLOAT_DIV = auto()
    MORE = auto()
    LESS = auto()
    MORE_OR_EQUAL = auto()
    LESS_OR_EQUAL = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    OPEN_PARANTH = auto()
    CLOSE_PARANTH = auto()
    BEGIN = auto()
    END = auto()
    DOT = auto()
    ID = auto()
    ASSIGN = auto()
    SEMI = auto()
    VAR = auto()
    PROCEDURE = auto()
    FUNCTION = auto()
    EXIT = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    EOF = auto()

    def __str__(self) -> str:
        return f"Token.{self.name}"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True, slots=True)
class Token:
    token_type: TokenType
    value: str = ""

    def __str__(self) -> str:
        return f"Token({self.token_type.name}" + (
            f", {self.value})" if self.value else ")"
        )

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def program(cls) -> "Token":
        return Token(TokenType.PROGRAM, "PROGRAM")

    @classmethod
    def var(cls) -> "Token":
        return Token(TokenType.VAR, "VAR")

    @classmethod
    def plus(cls) -> "Token":
        return Token(TokenType.PLUS, "+")

    @classmethod
    def minus(cls) -> "Token":
        return Token(TokenType.MINUS, "-")

    @classmethod
    def mult(cls) -> "Token":
        return Token(TokenType.MULTIPLICATION, "*")

    @classmethod
    def int_div(cls) -> "Token":
        return Token(TokenType.INTEGER_DIV, "DIV")

    @classmethod
    def float_div(cls) -> "Token":
        return Token(TokenType.FLOAT_DIV, "/")

    @classmethod
    def const_int(cls, value: str) -> "Token":
        return Token(TokenType.INTEGER_CONST, value)

    @classmethod
    def const_float(cls, value: str) -> "Token":
        return Token(TokenType.REAL_CONST, value)

    @classmethod
    def const_bool(cls, value: bool) -> "Token":
        return Token(TokenType.BOOLEAN_CONST, str(value).upper())

    @classmethod
    def integer(cls) -> "Token":
        return Token(TokenType.INTEGER, "INTEGER")

    @classmethod
    def boolean(cls) -> "Token":
        return Token(TokenType.BOOLEAN, "BOOLEAN")

    @classmethod
    def real(cls) -> "Token":
        return Token(TokenType.REAL, "REAL")

    @classmethod
    def colon(cls) -> "Token":
        return Token(TokenType.COLON, ":")

    @classmethod
    def comma(cls) -> "Token":
        return Token(TokenType.COMMA, ",")

    @classmethod
    def eof(cls) -> "Token":
        return Token(TokenType.EOF)

    @classmethod
    def open_p(cls) -> "Token":
        return Token(TokenType.OPEN_PARANTH, "(")

    @classmethod
    def close_p(cls) -> "Token":
        return Token(TokenType.CLOSE_PARANTH, ")")

    @classmethod
    def begin(cls) -> "Token":
        return Token(TokenType.BEGIN, "BEGIN")

    @classmethod
    def end(cls) -> "Token":
        return Token(TokenType.END, "END")

    @classmethod
    def dot(cls) -> "Token":
        return Token(TokenType.DOT, ".")

    @classmethod
    def Id(cls, variable_name: str) -> "Token":
        return Token(TokenType.ID, variable_name)

    @classmethod
    def semi(cls) -> "Token":
        return Token(TokenType.SEMI, ";")

    @classmethod
    def assign(cls) -> "Token":
        return Token(TokenType.ASSIGN, ":=")

    @classmethod
    def procedure(cls) -> "Token":
        return Token(TokenType.PROCEDURE, "PROCEDURE")

    @classmethod
    def function(cls) -> "Token":
        return Token(TokenType.FUNCTION, "FUNCTION")

    @classmethod
    def exit(cls) -> "Token":
        return Token(TokenType.EXIT, "EXIT")

    @classmethod
    def eq(cls) -> "Token":
        return Token(TokenType.EQUAL, "=")

    @classmethod
    def neq(cls) -> "Token":
        return Token(TokenType.NOT_EQUAL, "<>")

    @classmethod
    def gt(cls) -> "Token":
        return Token(TokenType.MORE, ">")

    @classmethod
    def get(cls) -> "Token":
        return Token(TokenType.MORE_OR_EQUAL, ">=")

    @classmethod
    def lt(cls) -> "Token":
        return Token(TokenType.LESS, "<")

    @classmethod
    def let(cls) -> "Token":
        return Token(TokenType.LESS_OR_EQUAL, "<=")

    @classmethod
    def And(cls) -> "Token":
        return Token(TokenType.AND, "AND")

    @classmethod
    def Or(cls) -> "Token":
        return Token(TokenType.OR, "OR")

    @classmethod
    def Not(cls) -> "Token":
        return Token(TokenType.NOT, "NOT")

    @classmethod
    def If(cls) -> "Token":
        return Token(TokenType.IF, "IF")

    @classmethod
    def then(cls) -> "Token":
        return Token(TokenType.THEN, "THEN")

    @classmethod
    def Else(cls) -> "Token":
        return Token(TokenType.ELSE, "ELSE")

    @classmethod
    def char(cls) -> "Token":
        return Token(TokenType.CHAR, "CHAR")

    @classmethod
    def string(cls) -> "Token":
        return Token(TokenType.STRING, "STRING")

    @classmethod
    def const_char(cls, value: str) -> "Token":
        assert len(value) == 1
        return Token(TokenType.CHAR_CONST, value)

    @classmethod
    def const_string(cls, value: str) -> "Token":
        return Token(TokenType.STRING_CONST, value)

    @classmethod
    def While(cls) -> "Token":
        return Token(TokenType.WHILE, "WHILE")

    @classmethod
    def do(cls) -> "Token":
        return Token(TokenType.DO, "DO")
