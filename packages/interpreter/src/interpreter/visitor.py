from abc import ABC, abstractmethod
from typing import Any

from interpreter.symbols import Symbol
from parser import AST, Block, Param, Call, Program

from parser import (
    Assign,
    Compound,
    NoOp,
    BinOp,
    Procedure,
    UnaryOp,
    Var,
    VarDecl,
)
from parser.parser import (
    Array,
    AssignIndex,
    Break,
    Condition,
    ConstDecl,
    Continue,
    DynamicArray,
    Enum,
    Exit,
    ForInStatement,
    ForStatement,
    Function,
    IfStatement,
    IndexOf,
    Literal,
    Range,
    StandardType,
    TypeDecl,
    WhileStatement,
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
    def visit_Exit(self, node: Exit) -> None: ...

    @abstractmethod
    def visit_Program(self, node: Program) -> None: ...

    @abstractmethod
    def visit_Block(self, node: Block) -> None: ...

    def visit_NoOp(self, node: NoOp) -> None:
        return None

    @abstractmethod
    def visit_Procedure(self, node: Procedure) -> Any: ...

    @abstractmethod
    def visit_Function(self, node: Function) -> Any: ...

    @abstractmethod
    def visit_BinOp(self, node: BinOp) -> Any: ...

    @abstractmethod
    def visit_Compound(self, node: Compound) -> Any: ...

    @abstractmethod
    def visit_VarDecl(self, node: VarDecl) -> Any: ...

    @abstractmethod
    def visit_StandardType(self, node: StandardType) -> Any: ...

    @abstractmethod
    def visit_Assign(self, node: Assign) -> Any: ...

    @abstractmethod
    def visit_Literal(self, node: Literal[Any, Symbol]) -> Any: ...

    @abstractmethod
    def visit_Var(self, node: Var) -> Any: ...

    @abstractmethod
    def visit_UnaryOp(self, node: UnaryOp) -> Any: ...

    @abstractmethod
    def visit_Param(self, node: Param) -> Any: ...

    @abstractmethod
    def visit_Call(self, node: Call[Symbol]) -> Any: ...

    @abstractmethod
    def visit_IfStatement(self, node: IfStatement) -> Any: ...

    @abstractmethod
    def visit_Condition(self, node: Condition) -> Any: ...

    @abstractmethod
    def visit_WhileStatement(self, node: WhileStatement) -> None: ...

    @abstractmethod
    def visit_ForStatement(self, node: ForStatement) -> None: ...

    @abstractmethod
    def visit_Continue(self, node: Continue) -> None: ...

    @abstractmethod
    def visit_Break(self, node: Break) -> None: ...

    @abstractmethod
    def visit_TypeDecl(self, node: TypeDecl[Symbol]) -> None: ...

    @abstractmethod
    def visit_ConstDecl(self, node: ConstDecl[Symbol]) -> None: ...

    @abstractmethod
    def visit_Range(self, node: Range[Symbol]) -> Any: ...

    @abstractmethod
    def visit_Enum(self, node: Enum[Symbol]) -> Any: ...

    @abstractmethod
    def visit_Array(self, node: Array[Symbol]) -> Any: ...

    @abstractmethod
    def visit_IndexOf(self, node: IndexOf[Symbol]) -> Any: ...

    @abstractmethod
    def visit_AssignIndex(self, node: AssignIndex[Symbol]) -> Any: ...

    @abstractmethod
    def visit_ForInStatement(self, node: ForInStatement[Symbol]) -> None: ...

    @abstractmethod
    def visit_DynamicArray(self, node: DynamicArray[Symbol]) -> Any: ...
