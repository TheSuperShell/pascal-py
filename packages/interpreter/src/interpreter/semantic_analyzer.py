from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Any, override

from parser import (
    AST,
    Assign,
    BinOp,
    Block,
    Compound,
    Num,
    Param,
    Procedure,
    ProcedureCall,
    ProcedureSymbol,
    Program,
    ProgramSymbol,
    UnaryOp,
    Var,
    VarDecl,
    Type,
    VarSymbol,
)
from interpreter.visitor import Visitor
from parser.parser import Exit
from parser.scoped_symbol_table import ScopedSymbolTable


class ErrorCode(IntEnum):
    DUPLICATE_VARIABLE = auto()
    ID_NOT_FOUND = auto()
    INCORRECT_CALL_TYPE = auto()
    INCORRECT_NUMBER_OF_INPUTS = auto()


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


@dataclass(slots=True)
class SymbolTableVisitor(Visitor):
    current_scope: ScopedSymbolTable | None = field(
        default_factory=ScopedSymbolTable.create_builtin_scope
    )

    def get_current_scope(self) -> ScopedSymbolTable:
        assert self.current_scope
        return self.current_scope

    @override
    def visit_Program(self, node: Program) -> Any:
        program_name = node.name
        self.get_current_scope().define(VarSymbol(program_name, ProgramSymbol()))
        print("ENTER scope: global")
        global_scope = ScopedSymbolTable(
            "global", scope_level=1, enclosing_sope=self.current_scope
        )
        self.current_scope = global_scope
        self.visit(node.block)
        print(global_scope)
        self.current_scope = self.current_scope.enclosing_scope
        print("LEAVE scope: global")

    @override
    def visit_Block(self, node: Block) -> Any:
        for decls in node.declarations:
            self.visit(decls)
        return self.visit(node.compund_statement)

    @override
    def visit_Compound(self, node: Compound) -> Any:
        for child in node.children:
            if isinstance(child, Exit):
                print(f"EXIT {self.get_current_scope().scope_name}")
                return
            self.visit(child)

    @override
    def visit_Procedure(self, node: Procedure) -> Any:
        proc_name = node.name
        proc_symbol = ProcedureSymbol(proc_name)
        self.get_current_scope().define(proc_symbol)

        print(f"ENTER scope: {proc_name}")
        procedure_scope = ScopedSymbolTable(
            proc_name,
            scope_level=(self.current_scope.scope_level if self.current_scope else 0)
            + 1,
            enclosing_sope=self.current_scope,
        )
        self.current_scope = procedure_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.define(var_symbol)
            proc_symbol.params.append(var_symbol)

        self.visit(node.block)
        print(procedure_scope)
        self.current_scope = self.current_scope.enclosing_scope
        print(f"LEAVE scope: {proc_name}")

        proc_symbol.block_ast = node.block

    @override
    def visit_Num(self, node: Num) -> Any:
        return

    @override
    def visit_Assign(self, node: Assign) -> Any:
        self.visit(node.left)
        self.visit(node.right)

    @override
    def visit_Var(self, node: Var) -> Any:
        var_name = node.value
        var_symbol = self.get_current_scope().lookup(var_name)
        if var_symbol is None:
            raise SemanticError(
                f"symbol not found {var_name}", ErrorCode.ID_NOT_FOUND, node
            )
        return

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return self.visit(node.expr)

    @override
    def visit_VarDecl(self, node: VarDecl) -> Any:
        type_name = node.type_node.value
        type_symbol = self.get_current_scope().lookup(type_name)

        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        if (
            self.get_current_scope().lookup(var_name, current_scope_only=True)
            is not None
        ):
            raise SemanticError(
                f"duplicate identifier {var_name} found",
                ErrorCode.DUPLICATE_VARIABLE,
                node,
            )
        self.get_current_scope().define(var_symbol)

    @override
    def visit_Type(self, node: Type) -> Any:
        return

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        self.visit(node.left)
        self.visit(node.right)
        return None

    @override
    def visit_Param(self, node: Param) -> Any:
        return None

    @override
    def visit_ProcedureCall(self, node: ProcedureCall) -> Any:
        proc_name = node.proc_name
        proc_symbol = self.get_current_scope().lookup(proc_name)
        node.proc_symbol = proc_symbol
        if proc_symbol is None:
            raise SemanticError(
                f"no procedure found: {proc_name}", ErrorCode.ID_NOT_FOUND, node
            )
        if not isinstance(proc_symbol, ProcedureSymbol):
            raise SemanticError(
                f"found {proc_name}, but it's not a procedure: {proc_symbol}",
                ErrorCode.INCORRECT_CALL_TYPE,
                node,
            )
        if len(proc_symbol.params) != len(node.actual_params):
            raise SemanticError(
                f"procedure {proc_name} expected "
                f"{len(proc_symbol.params)} number of inputs, "
                f"found {len(node.actual_params)}",
                ErrorCode.INCORRECT_NUMBER_OF_INPUTS,
                node,
            )
        for param_node in node.actual_params:
            self.visit(param_node)
