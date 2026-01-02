from dataclasses import dataclass, field
from typing import Any, override

from src.parser import Assign, BinOp, Num, UnaryOp, Var, VarDecl, Type
from src.symbols import ScopedSymbolTable, VarSymbol
from src.visitor import Visitor


@dataclass(slots=True)
class SymbolTableVisitor(Visitor):
    symtab: ScopedSymbolTable = field(
        default=ScopedSymbolTable("global", scope_level=1)
    )

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
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(f"symbol not found {var_name}")
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

        if self.symtab.lookup(var_name) is not None:
            raise Exception(f"duplicate identifier {var_name} found")
        self.symtab.define(var_symbol)

    @override
    def visit_Type(self, node: Type) -> Any:
        return

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        self.visit(node.left)
        self.visit(node.right)
        return None
