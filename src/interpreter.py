from collections.abc import Callable
from src.parser import AST, Num, Parser, BinOp
from src.token import TokenType


class InterpreterError(Exception): ...


_OPERATIONS: dict[TokenType, Callable[[int, int], int]] = {
    TokenType.PLUS: lambda x, y: x + y,
    TokenType.MINUS: lambda x, y: x - y,
    TokenType.MULTIPLICATION: lambda x, y: x * y,
    TokenType.DIVISION: lambda x, y: x // y,
}


class Interpreter:
    __slots__ = "parser"

    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def visit(self, node: AST) -> int:
        if isinstance(node, Num):
            return node.value
        if not isinstance(node, BinOp):
            raise NotImplementedError()
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _OPERATIONS[node.op.token_type](left, right)

    def interpret(self) -> int:
        tree = self.parser.parse()
        return self.visit(tree)
