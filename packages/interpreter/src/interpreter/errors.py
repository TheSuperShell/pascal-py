from parser.errors import ErrorCode
from parser.parser import AST


class InterpreterError(Exception):
    def __init__(self, message: str, error_code: ErrorCode | None = None) -> None:
        self.message = message
        self.error_code = error_code


class SemanticError(Exception):
    def __init__(
        self,
        message: str | None = None,
        error_code: ErrorCode | None = None,
        node: AST | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.node = node
