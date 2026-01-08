from dataclasses import dataclass, field
from typing import Any, override
from parser import (
    AST,
    Assign,
    BinOp,
    Block,
    Compound,
    NoOp,
    Num,
    Param,
    Procedure,
    ProcedureCall,
    Program,
    Type,
    UnaryOp,
    Var,
    VarDecl,
    VarSymbol,
)
from interpreter.visitor import Visitor
from parser.scoped_symbol_table import ScopedSymbolTable


@dataclass(slots=True)
class S2SCompiler(Visitor):
    current_scope: ScopedSymbolTable | None = field(
        default_factory=ScopedSymbolTable.create_builtin_scope
    )

    def get_current_scope(self) -> ScopedSymbolTable:
        assert self.current_scope
        return self.current_scope

    @property
    def tabs(self) -> str:
        return "    " * self.get_current_scope().scope_level

    @property
    def tabs_previous(self) -> str:
        return "    " * max(0, self.get_current_scope().scope_level - 1)

    @override
    def visit_Program(self, node: Program) -> Any:
        program_name = node.name
        output = []
        output.append(f"program {program_name}0;")

        global_scope = ScopedSymbolTable(
            "global", scope_level=1, enclosing_sope=self.current_scope
        )
        self.current_scope = global_scope

        output.extend(self.visit(node.block))
        output.append(f"end. {{END OF {program_name}}}")  # "

        self.current_scope = self.current_scope.enclosing_scope
        return output

    @override
    def visit_Block(self, node: Block) -> Any:
        results = []
        for decls in node.declarations:
            if isinstance(decls, VarDecl):
                dec = self.visit(decls)
                results.append(self.tabs + dec)
            else:
                results.extend(self.visit(decls))
        results.append(f"{self.tabs_previous}begin")
        results.extend(self.visit(node.compund_statement))
        return results

    @override
    def visit_Compound(self, node: Compound) -> Any:
        results = []
        for child in node.children:
            if isinstance(child, NoOp):
                continue
            results.append(self.tabs + self.visit(child) + ";")
        if len(results) == 0:
            results.append("")
        return results

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        result = [self.visit(node.left)]
        result.append(node.token.value)
        result.append(self.visit(node.right))
        return " ".join(result)

    @override
    def visit_Assign(self, node: Assign) -> Any:
        result = [self.visit(node.left)]
        result.append(":=")
        result.append(self.visit(node.right))
        return " ".join(result)

    @override
    def visit_NoOp(self, node: NoOp) -> Any:
        return ""

    @override
    def visit_Num(self, node: Num) -> Any:
        return str(node.value)

    @override
    def visit_Procedure(self, node: Procedure) -> Any:
        proc_name = node.name
        previous_scope_level = self.get_current_scope().scope_level
        proc_scope = ScopedSymbolTable(
            proc_name,
            scope_level=previous_scope_level + 1,
            enclosing_sope=self.current_scope,
        )
        self.current_scope = proc_scope
        # procedure_symbol = ProcedureSymbol(proc_name)
        params = []
        for param in node.params:
            params.append(self.visit(param))
        result = [
            f"{self.tabs_previous}procedure {proc_name}{previous_scope_level}({'; '.join(params)});"
        ]
        result.extend(self.visit(node.block))
        result.append(f"{self.tabs_previous}end; {{END OF {proc_name}}}")
        self.current_scope = self.get_current_scope().enclosing_scope
        return result

    @override
    def visit_Param(self, node: Param) -> Any:
        var_name = node.var_node.value
        var_type = node.type_node.value
        current_scope = self.get_current_scope().scope_level
        type_symbol = self.get_current_scope().lookup(var_type)
        if type_symbol is None:
            raise Exception(f"unkown type {var_type}")
        self.get_current_scope().define(VarSymbol(var_name, type_symbol))
        return f"{var_name}{current_scope} : {self.visit(node.type_node)}"

    @override
    def visit_Type(self, node: Type) -> Any:
        return str(node.value)

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return node.token.value + f" {self.visit(node.expr)}"

    @override
    def visit_Var(self, node: Var) -> Any:
        var_name = node.value
        var_symbol, scope_level = self.get_current_scope().lookup_with_scope(var_name)
        if var_symbol is None:
            raise Exception(f"unkown variable {var_name}")
        return f"<{var_name}{scope_level}:{var_symbol.symbol_type.name if var_symbol.symbol_type else None}>"

    @override
    def visit_VarDecl(self, node: VarDecl) -> Any:
        var_name = node.var_node.value
        scope_level = self.get_current_scope().scope_level
        var_type = node.type_node.value
        type_symbol = self.get_current_scope().lookup(var_type)
        if type_symbol is None:
            raise Exception(f"unkown type {var_type}")
        self.get_current_scope().define(VarSymbol(var_name, type_symbol))
        return f"var {var_name}{scope_level} : {var_type};"

    @override
    def visit_ProcedureCall(self, node: ProcedureCall) -> Any:
        return ""

    def build_output(self, node: AST) -> str:
        output = self.visit(node)
        return "\n".join(output)
