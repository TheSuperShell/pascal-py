from dataclasses import dataclass, field
from typing import Any, override

from src.parser import (
    Assign,
    BinOp,
    Num,
    Procedure,
    Program,
    UnaryOp,
    Var,
    VarDecl,
    Type,
)
from src.symbols import ProcedureSymbol, ProgramSymbol, ScopedSymbolTable, VarSymbol
from src.visitor import Visitor


class SemanticError(Exception): ...


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
            raise NameError(f"symbol not found {var_name}")
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
            raise SemanticError(f"duplicate identifier {var_name} found")
        self.get_current_scope().define(var_symbol)

    @override
    def visit_Type(self, node: Type) -> Any:
        return

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        self.visit(node.left)
        self.visit(node.right)
        return None
