from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Self


class TokenType(StrEnum):
    # keywords (until EOF)
    PROGRAM = auto()
    INTEGER = auto()
    REAL = auto()
    BOOLEAN = auto()
    CHAR = auto()
    STRING = auto()
    INTEGER_DIV = "DIV"
    AND = auto()
    OR = auto()
    NOT = auto()
    BEGIN = auto()
    END = auto()
    VAR = auto()
    PROCEDURE = auto()
    FUNCTION = auto()
    EXIT = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    TO = auto()
    CONTINUE = auto()
    BREAK = auto()
    TYPE = auto()
    CONST = auto()
    ARRAY = auto()
    OF = auto()
    IN = auto()
    OUT = auto()
    COMMA = ","
    PLUS = "+"
    MINUS = "-"
    MULTIPLICATION = "*"
    FLOAT_DIV = "/"
    EQUAL = "="
    OPEN_PARANTH = "("
    CLOSE_PARANTH = ")"
    DOT = "."
    SEMI = ";"
    OPEN_BRACKET = "["
    CLOSE_BRACKET = "]"
    EOF = auto()

    # token with value
    INTEGER_CONST = auto()
    REAL_CONST = auto()
    BOOLEAN_CONST = auto()
    CHAR_CONST = auto()
    STRING_CONST = auto()
    ID = auto()

    # special chars
    MORE = ">"
    LESS = "<"
    MORE_OR_EQUAL = ">="
    LESS_OR_EQUAL = "<="
    NOT_EQUAL = "<>"
    COLON = ":"
    ASSIGN = ":="

    def __str__(self) -> str:
        return f"Token.{self.name}"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def get_reserved_keywords() -> "dict[str, TokenType]":
        result = {}
        for token_type in TokenType:
            result[token_type.value.upper()] = token_type
            if token_type == TokenType.EOF:
                break
        return result


@dataclass(frozen=True, slots=True)
class Token:
    token_type: TokenType
    value: str
    lineno: int
    col: int

    def __str__(self) -> str:
        return f"Token({self.token_type.name}" + (
            f", {self.value})" if self.value else ")"
        )

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def new(cls, token_type: TokenType, lineno: int = 0, col: int = 0) -> Self:
        return cls(token_type, token_type.value, lineno, col)

    @classmethod
    def with_value(
        cls, token_type: TokenType, value: str, lieno: int = 0, col: int = 0
    ) -> Self:
        return cls(token_type, value, lieno, col)
