from dataclasses import dataclass
from enum import IntEnum, auto


class TokenType(IntEnum):
    INTEGER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLICATION = auto()
    DIVISION = auto()
    OPEN_PARANTH = auto()
    CLOSE_PARANTH = auto()
    BEGIN = auto()
    END = auto()
    DOT = auto()
    ID = auto()
    ASSIGN = auto()
    SEMI = auto()
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
    def plus(cls) -> "Token":
        return Token(TokenType.PLUS, "+")

    @classmethod
    def minus(cls) -> "Token":
        return Token(TokenType.MINUS, "-")

    @classmethod
    def mult(cls) -> "Token":
        return Token(TokenType.MULTIPLICATION, "*")

    @classmethod
    def div(cls) -> "Token":
        return Token(TokenType.DIVISION, "DIV")

    @classmethod
    def integer(cls, value: str) -> "Token":
        return Token(TokenType.INTEGER, value)

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
