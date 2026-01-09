from dataclasses import dataclass, field
from typing import Any, override

from interpreter.errors import SemanticError
from parser import (
    Assign,
    BinOp,
    Block,
    Compound,
    Num,
    Param,
    Procedure,
    Call,
    Program,
    ProgramSymbol,
    UnaryOp,
    Var,
    VarDecl,
    Type,
    VarSymbol,
)
from interpreter.visitor import Visitor
from parser.errors import ErrorCode
from parser.parser import (
    Bool,
    BuiltinCallableSymbol,
    BuiltinTypeSymbol,
    Condition,
    Exit,
    Function,
    CallableSymbol,
    IfStatement,
)
from parser.scoped_symbol_table import ScopeType, ScopedSymbolTable


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
            "global",
            ScopeType.PROGRAM,
            scope_level=1,
            enclosing_sope=self.current_scope,
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
    def visit_Exit(self, node: Exit) -> Any:
        if (
            self.get_current_scope().scope_type != ScopeType.FUNCTION
            and node.expr is not None
        ):
            raise SemanticError(
                "procedure or Program should not return anything",
                ErrorCode.INVALID_EXIT,
                node,
            )
        elif (
            self.get_current_scope().scope_type == ScopeType.FUNCTION
            and node.expr is None
        ):
            raise SemanticError(
                "function should return a value",
                ErrorCode.INVALID_EXIT,
                node,
            )
        print(f"EXIT {self.get_current_scope().scope_name}")
        if node.expr:
            self.visit(node.expr)

    @override
    def visit_Compound(self, node: Compound) -> Any:
        for child in node.children:
            self.visit(child)

    @override
    def visit_Function(self, node: Function) -> Any:
        func_name = node.name
        return_type = node.return_type
        return_symbol = self.get_current_scope().lookup(return_type.value)
        if return_symbol is None:
            raise SemanticError(
                f"return type {return_type.value} is unkown",
                ErrorCode.ID_NOT_FOUND,
                node,
            )
        assert isinstance(return_symbol, BuiltinTypeSymbol)
        func_symbol = CallableSymbol(func_name, return_symbol)
        self.get_current_scope().define(func_symbol)

        print(f"ENTER scope: {func_name}")
        function_scope = ScopedSymbolTable(
            func_name,
            ScopeType.FUNCTION,
            scope_level=(self.current_scope.scope_level if self.current_scope else 0)
            + 1,
            enclosing_sope=self.current_scope,
        )
        self.current_scope = function_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.define(var_symbol)
            func_symbol.params.append(var_symbol)

        self.current_scope.define(VarSymbol("result", return_symbol))

        self.visit(node.block)
        print(function_scope)
        self.current_scope = self.get_current_scope().enclosing_scope
        print(f"LEAVE scope: {func_name}")

        func_symbol.block_ast = node.block

    @override
    def visit_Procedure(self, node: Procedure) -> Any:
        proc_name = node.name
        proc_symbol = CallableSymbol(proc_name)
        self.get_current_scope().define(proc_symbol)

        print(f"ENTER scope: {proc_name}")
        procedure_scope = ScopedSymbolTable(
            proc_name,
            ScopeType.PROCEDURE,
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
    def visit_Bool(self, node: Bool) -> Any:
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
    def visit_Call(self, node: Call) -> Any:
        callable_name = node.name
        callable_symbol = self.get_current_scope().lookup(callable_name)
        node.proc_symbol = callable_symbol
        if callable_symbol is None:
            raise SemanticError(
                f"no callable found: {callable_name}", ErrorCode.ID_NOT_FOUND, node
            )
        if not (
            isinstance(callable_symbol, CallableSymbol)
            or isinstance(callable_symbol, BuiltinCallableSymbol)
        ):
            raise SemanticError(
                f"{callable_name} is not a callable",
                ErrorCode.INCORRECT_CALL_TYPE,
                node,
            )
        if callable_symbol.params is not None and len(callable_symbol.params) != len(
            node.actual_params
        ):
            raise SemanticError(
                f"{callable_name} expected "
                f"{len(callable_symbol.params)} number of inputs, "
                f"found {len(node.actual_params)}",
                ErrorCode.INCORRECT_NUMBER_OF_INPUTS,
                node,
            )
        for param_node in node.actual_params:
            self.visit(param_node)

    @override
    def visit_IfStatement(self, node: IfStatement) -> Any:
        self.visit(node.main_condition)
        for other_cond in node.secondary_conditions:
            self.visit(other_cond)
        if node.else_condition:
            self.visit(node.else_condition)
        return None

    @override
    def visit_Condition(self, node: Condition) -> Any:
        self.visit(node.condition)
        self.visit(node.expr)
