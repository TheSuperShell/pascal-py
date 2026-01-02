from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from src.parser import AST, Assign, Compund, NoOp, Num, Parser, BinOp, UnaryOp, Var
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


@dataclass(slots=True)
class Interpreter(TreeProcessor):
    parser: Parser
    global_scope: dict[str, Any] = field(default_factory=dict)

    def visit(self, node: AST) -> Any:
        if isinstance(node, NoOp):
            return
        if isinstance(node, Compund):
            for child in node.children:
                self.visit(child)
            return
        if isinstance(node, Assign):
            var_name = node.left.value
            self.global_scope[var_name] = self.visit(node.right)
            return
        if isinstance(node, Var):
            var_name = node.value
            val = self.global_scope.get(var_name)
            if val is None:
                raise NameError(repr(var_name))
            return val
        if isinstance(node, Num):
            return node.value
        if isinstance(node, UnaryOp):
            return _UNARY_OP[node.token.token_type](self.visit(node.expr))
        if isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            return _OPERATIONS[node.token.token_type](left, right)
        raise NotImplementedError(node)
