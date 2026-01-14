from enum import IntEnum, auto

from parser.token import Token


class ErrorCode(IntEnum):
    UNEXPECTED_TOKEN = auto()
    EOF_NOT_FOUND = auto()
    UNASSIGNED_VARIABLE = auto()
    DUPLICATE_VARIABLE = auto()
    ID_NOT_FOUND = auto()
    INCORRECT_CALL_TYPE = auto()
    INCORRECT_NUMBER_OF_INPUTS = auto()
    INCORRECT_INPUT_TYPE = auto()
    INVALID_EXIT = auto()
    NO_RETURN = auto()
    UNKOWN_TYPE = auto()
    INCORRECT_TYPE = auto()
    UNKOWN_BINARY_OPERATOR = auto()
    UNSUPPORTED_BINARY_OPERATION = auto()
    UNASSIGNABLE_TYPES = auto()
    OUTSIDE_LOOP = auto()
    ASSIGN_TO_CONST = auto()
    RANGE_OUT_OF_BOUNDS = auto()
    INDEX_OUT_OF_RANGE = auto()


class LexerError(Exception):
    def __init__(
        self, message: str | None = None, error_code: ErrorCode | None = None
    ) -> None:
        self.message = message
        self.error_code = error_code


class ParserError(Exception):
    def __init__(
        self,
        message: str | None = None,
        error_code: ErrorCode | None = None,
        token: Token | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.token = token
