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
