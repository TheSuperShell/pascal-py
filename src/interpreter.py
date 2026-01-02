from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, override
from src.parser import (
    Assign,
    Num,
    Parser,
    BinOp,
    Type,
    UnaryOp,
    Var,
    VarDecl,
)
from src.semantic_analyzer import SymbolTableVisitor
from src.token import TokenType
from src.visitor import Visitor


class InterpreterError(Exception): ...


_OPERATIONS: dict[TokenType, Callable[[int | float, int | float], int | float]] = {
    TokenType.PLUS: lambda x, y: x + y,
    TokenType.MINUS: lambda x, y: x - y,
    TokenType.MULTIPLICATION: lambda x, y: x * y,
    TokenType.INTEGER_DIV: lambda x, y: x // y,
    TokenType.FLOAT_DIV: lambda x, y: x / y,
}

_UNARY_OP: dict[TokenType, Callable[[int | float], int | float]] = {
    TokenType.PLUS: lambda x: x,
    TokenType.MINUS: lambda x: -x,
}


@dataclass(slots=True)
class DefaultVisitor(Visitor):
    global_scope: dict[str, Any] = field(default_factory=dict)

    @override
    def visit_Num(self, node: Num) -> Any:
        return node.value

    @override
    def visit_Assign(self, node: Assign) -> Any:
        var_name = node.left.value
        self.global_scope[var_name] = self.visit(node.right)
        return None

    @override
    def visit_Var(self, node: Var) -> Any:
        var_name = node.value
        val = self.global_scope.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        return val

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return _UNARY_OP[node.token.token_type](self.visit(node.expr))

    @override
    def visit_VarDecl(self, node: VarDecl) -> Any:
        return

    @override
    def visit_Type(self, node: Type) -> Any:
        return

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _OPERATIONS[node.token.token_type](left, right)


@dataclass(slots=True)
class Interpreter:
    parser: Parser
    semanti_analyzer: Visitor = field(default_factory=SymbolTableVisitor)
    default_visitor: Visitor = field(default_factory=DefaultVisitor)

    def process(self) -> Any:
        tree = self.parser.parse()
        self.semanti_analyzer.visit(tree)
        return self.default_visitor.visit(tree)
