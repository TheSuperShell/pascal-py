from abc import ABC, abstractmethod
from typing import Any

from src.parser import AST, Block, Param, ProcedureCall, Program

from src.parser import (
    Assign,
    Compound,
    NoOp,
    Num,
    BinOp,
    Procedure,
    Type,
    UnaryOp,
    Var,
    VarDecl,
)


class Visitor(ABC):
    def visit(self, node: AST) -> Any:
        type_name = type(node).__name__
        method_name = f"visit_{type_name}"
        method = getattr(self, method_name)
        if method is None:
            raise NotImplementedError(node)
        return method(node)

    @abstractmethod
    def visit_Program(self, node: Program) -> Any: ...

    @abstractmethod
    def visit_Block(self, node: Block) -> Any: ...

    def visit_NoOp(self, node: NoOp) -> Any:
        return None

    @abstractmethod
    def visit_Procedure(self, node: Procedure) -> Any: ...

    @abstractmethod
    def visit_BinOp(self, node: BinOp) -> Any: ...

    @abstractmethod
    def visit_Compound(self, node: Compound) -> Any: ...

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

    @abstractmethod
    def visit_Param(self, node: Param) -> Any: ...

    @abstractmethod
    def visit_ProcedureCall(self, node: ProcedureCall) -> Any: ...
