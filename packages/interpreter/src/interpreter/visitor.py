from abc import ABC, abstractmethod

from interpreter.symbols import PythonTypes, Symbol
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


class Visitor[T](ABC):
    def visit(self, node: AST[Symbol]) -> T | None:
        type_name = type(node).__name__
        method_name = f"visit_{type_name}"
        method = getattr(self, method_name)
        if method is None:
            raise NotImplementedError(node)
        return method(node)

    def visit_not_none(self, node: AST[Symbol]) -> T:
        result = self.visit(node)
        assert result is not None
        return result

    @abstractmethod
    def visit_Exit(self, node: Exit[Symbol]) -> None: ...

    @abstractmethod
    def visit_Program(self, node: Program[Symbol]) -> None: ...

    @abstractmethod
    def visit_Block(self, node: Block[Symbol]) -> None: ...

    def visit_NoOp(self, node: NoOp[Symbol]) -> None:
        return None

    @abstractmethod
    def visit_Procedure(self, node: Procedure[Symbol]) -> None: ...

    @abstractmethod
    def visit_Function(self, node: Function[Symbol]) -> None: ...

    @abstractmethod
    def visit_BinOp(self, node: BinOp[Symbol]) -> T: ...

    @abstractmethod
    def visit_Compound(self, node: Compound[Symbol]) -> None: ...

    @abstractmethod
    def visit_VarDecl(self, node: VarDecl[Symbol]) -> None: ...

    @abstractmethod
    def visit_StandardType(self, node: StandardType[Symbol]) -> T: ...

    @abstractmethod
    def visit_Assign(self, node: Assign[Symbol]) -> None: ...

    @abstractmethod
    def visit_Literal(self, node: Literal[PythonTypes, Symbol]) -> T: ...

    @abstractmethod
    def visit_Var(self, node: Var[Symbol]) -> T: ...

    @abstractmethod
    def visit_UnaryOp(self, node: UnaryOp[Symbol]) -> T: ...

    @abstractmethod
    def visit_Param(self, node: Param[Symbol]) -> T: ...

    @abstractmethod
    def visit_Call(self, node: Call[Symbol]) -> T | None: ...

    @abstractmethod
    def visit_IfStatement(self, node: IfStatement[Symbol]) -> None: ...

    @abstractmethod
    def visit_Condition(self, node: Condition[Symbol]) -> None: ...

    @abstractmethod
    def visit_WhileStatement(self, node: WhileStatement[Symbol]) -> None: ...

    @abstractmethod
    def visit_ForStatement(self, node: ForStatement[Symbol]) -> None: ...

    @abstractmethod
    def visit_Continue(self, node: Continue[Symbol]) -> None: ...

    @abstractmethod
    def visit_Break(self, node: Break[Symbol]) -> None: ...

    @abstractmethod
    def visit_TypeDecl(self, node: TypeDecl[Symbol]) -> None: ...

    @abstractmethod
    def visit_ConstDecl(self, node: ConstDecl[Symbol]) -> None: ...

    @abstractmethod
    def visit_Range(self, node: Range[Symbol]) -> T: ...

    @abstractmethod
    def visit_Enum(self, node: Enum[Symbol]) -> T: ...

    @abstractmethod
    def visit_Array(self, node: Array[Symbol]) -> T: ...

    @abstractmethod
    def visit_IndexOf(self, node: IndexOf[Symbol]) -> T: ...

    @abstractmethod
    def visit_AssignIndex(self, node: AssignIndex[Symbol]) -> None: ...

    @abstractmethod
    def visit_ForInStatement(self, node: ForInStatement[Symbol]) -> None: ...

    @abstractmethod
    def visit_DynamicArray(self, node: DynamicArray[Symbol]) -> T: ...
