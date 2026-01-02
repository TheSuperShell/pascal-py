from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, override
from src.parser import (
    AST,
    Assign,
    Block,
    Compound,
    NoOp,
    Num,
    Parser,
    BinOp,
    Program,
    Type,
    UnaryOp,
    Var,
    VarDecl,
)
from src.symbols import SymbolTable, VarSymbol
from src.token import TokenType


class InterpreterError(Exception): ...


class Visitor(ABC):
    def visit(self, node: AST) -> Any:
        type_name = type(node).__name__
        method_name = f"visit_{type_name}"
        method = getattr(self, method_name)
        if method is None:
            raise NotImplementedError(node)
        return method(node)

    def visit_Program(self, node: Program) -> Any:
        return self.visit(node.block)

    def visit_Block(self, node: Block) -> Any:
        for decl in node.declarations:
            self.visit(decl)
        return self.visit(node.compund_statement)

    def visit_NoOp(self, node: NoOp) -> Any:
        return None

    @abstractmethod
    def visit_BinOp(self, node: BinOp) -> Any: ...

    def visit_Compound(self, node: Compound) -> Any:
        for child in node.children:
            self.visit(child)
        return None

    @abstractmethod
    def visit_VarDecl(self, node: VarDecl) -> Any: ...

    @abstractmethod
    def visit_Type(self, node: Type) -> Any: ...

    @abstractmethod
    def visit_Assign(self, node: Assign) -> Any: ...

    @abstractmethod
    def visit_Num(self, node: Num) -> Any: ...

    @abstractmethod
    def visit_Var(self, node: Var) -> Any: ...

    @abstractmethod
    def visit_UnaryOp(self, node: UnaryOp) -> Any: ...


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
class SymbolTableVisitor(Visitor):
    symtab: SymbolTable = field(default_factory=SymbolTable)

    @override
    def visit_Num(self, node: Num) -> Any:
        return

    @override
    def visit_Assign(self, node: Assign) -> Any:
        var_name = node.left.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))
        return self.visit(node.right)

    @override
    def visit_Var(self, node: Var) -> Any:
        var_name = node.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))
        return

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return self.visit(node.expr)

    @override
    def visit_VarDecl(self, node: VarDecl) -> Any:
        type_name = node.type_node.value
        type_symbol = self.symtab.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.symtab.define(var_symbol)

    @override
    def visit_Type(self, node: Type) -> Any:
        return

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        self.visit(node.left)
        self.visit(node.right)
        return None


@dataclass(slots=True)
class Interpreter:
    parser: Parser
    visitor: Visitor = field(default_factory=SymbolTableVisitor)

    def process(self) -> Any:
        tree = self.parser.parse()
        return self.visitor.visit(tree)
