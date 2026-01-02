from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from src.parser import AST, Num, Parser, BinOp, UnaryOp
from src.token import TokenType


class InterpreterError(Exception): ...


class TreeProcessor(ABC):
    __slots__ = "parser"

    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    @abstractmethod
    def visit(self, node: AST) -> Any: ...

    def process(self) -> Any:
        tree = self.parser.parse()
        return self.visit(tree)


_OPERATIONS: dict[TokenType, Callable[[int, int], int]] = {
    TokenType.PLUS: lambda x, y: x + y,
    TokenType.MINUS: lambda x, y: x - y,
    TokenType.MULTIPLICATION: lambda x, y: x * y,
    TokenType.DIVISION: lambda x, y: x // y,
}

_UNARY_OP: dict[TokenType, Callable[[int], int]] = {
    TokenType.PLUS: lambda x: x,
    TokenType.MINUS: lambda x: -x,
}


class Interpreter(TreeProcessor):
    def visit(self, node: AST) -> int:
        if isinstance(node, Num):
            return node.value
        if isinstance(node, UnaryOp):
            return _UNARY_OP[node.op.token_type](self.visit(node.expr))
        if not isinstance(node, BinOp):
            raise NotImplementedError()
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _OPERATIONS[node.op.token_type](left, right)
