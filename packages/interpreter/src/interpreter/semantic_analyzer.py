from dataclasses import dataclass
import logging
from typing import Any, Self, override

from interpreter.builtins import BuiltinTypes
from interpreter.errors import SemanticError
from interpreter.symbols import (
    BuiltinCallableSymbol,
    BuiltinTypeSymbol,
    CallableSymbol,
    ProgramSymbol,
    Symbol,
    VarSymbol,
)
from interpreter.utils import ScopeType, ScopedSymbolTable
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
    UnaryOp,
    Var,
    VarDecl,
    Type,
)
from interpreter.visitor import Visitor
from parser.errors import ErrorCode
from parser.parser import (
    AST,
    Bool,
    Condition,
    Exit,
    Function,
    IfStatement,
    Str,
)
from parser.token import TokenType


@dataclass(slots=True)
class SymbolTableVisitor(Visitor):
    logger: logging.Logger
    current_scope: ScopedSymbolTable | None = None

    @classmethod
    def new(cls, logger: logging.Logger) -> Self:
        return cls(logger, ScopedSymbolTable.create_builtin_scope(logger))

    def get_current_scope(self) -> ScopedSymbolTable:
        assert self.current_scope
        return self.current_scope

    @override
    def visit_Program(self, node: Program) -> Any:
        program_name = node.name
        self.get_current_scope().define(VarSymbol(program_name, ProgramSymbol()))
        self.logger.debug("ENTER scope: global")
        global_scope = ScopedSymbolTable(
            "global",
            ScopeType.PROGRAM,
            scope_level=1,
            enclosing_scope=self.current_scope,
            logger=self.logger,
        )
        self.current_scope = global_scope
        self.visit(node.block)
        self.logger.debug(global_scope)
        self.current_scope = self.current_scope.enclosing_scope
        self.logger.debug("LEAVE scope: global")

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
        self.logger.debug(f"EXIT {self.get_current_scope().scope_name}")
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
        self.get_current_scope().define_callable(func_symbol)

        self.logger.debug(f"ENTER scope: {func_name}")
        function_scope = ScopedSymbolTable(
            func_name,
            ScopeType.FUNCTION,
            scope_level=(self.current_scope.scope_level if self.current_scope else 0)
            + 1,
            enclosing_scope=self.current_scope,
            logger=self.logger,
        )
        self.current_scope = function_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.define(var_symbol)
            func_symbol.params.append(var_symbol)

        result_exists = self.current_scope.lookup("result", current_scope_only=True)
        func_var_exists = self.current_scope.lookup(func_name, current_scope_only=True)
        if result_exists is not None or func_var_exists is not None:
            raise SemanticError(
                f"result and {func_name} are special symbols and cannot be overridden: {result_exists=}, {func_var_exists=}",
                ErrorCode.DUPLICATE_VARIABLE,
                node,
            )
        self.current_scope.define(VarSymbol("result", return_symbol))
        self.current_scope.define(VarSymbol(func_name, return_symbol))

        self.visit(node.block)
        self.logger.debug(function_scope)
        self.current_scope = self.get_current_scope().enclosing_scope
        self.logger.debug(f"LEAVE scope: {func_name}")

        func_symbol.block_ast = node.block

    @override
    def visit_Procedure(self, node: Procedure) -> Any:
        proc_name = node.name
        proc_symbol = CallableSymbol(proc_name)
        self.get_current_scope().define_callable(proc_symbol)

        self.logger.debug(f"ENTER scope: {proc_name}")
        procedure_scope = ScopedSymbolTable(
            proc_name,
            ScopeType.PROCEDURE,
            scope_level=(self.current_scope.scope_level if self.current_scope else 0)
            + 1,
            enclosing_scope=self.current_scope,
            logger=self.logger,
        )
        self.current_scope = procedure_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.define(var_symbol)
            proc_symbol.params.append(var_symbol)

        self.visit(node.block)
        self.logger.debug(procedure_scope)
        self.current_scope = self.current_scope.enclosing_scope
        self.logger.debug(f"LEAVE scope: {proc_name}")

        proc_symbol.block_ast = node.block

    @override
    def visit_Num(self, node: Num) -> Symbol:
        return BuiltinTypes.REAL.value

    @override
    def visit_Bool(self, node: Bool) -> Symbol:
        return BuiltinTypes.BOOLEAN.value

    @override
    def visit_Assign(self, node: Assign) -> Any:
        self.visit(node.left)
        self.visit(node.right)

    @override
    def visit_Var(self, node: Var) -> Symbol:
        var_name = node.value
        var_symbol = self.get_current_scope().lookup(var_name)
        if var_symbol is None:
            raise SemanticError(
                f"symbol not found {var_name}", ErrorCode.ID_NOT_FOUND, node
            )
        if var_symbol.symbol_type is None:
            raise SemanticError(
                f"unkown type for variable {var_symbol}", ErrorCode.UNKOWN_TYPE, node
            )
        return var_symbol.symbol_type

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> Symbol:
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
    def visit_Type(self, node: Type) -> Symbol:
        type_symbol = self.get_current_scope().lookup(node.value)
        if type_symbol is None:
            raise SemanticError(
                f"unkown type {node.value}", ErrorCode.UNKOWN_TYPE, node
            )
        return type_symbol

    @override
    def visit_BinOp(self, node: BinOp) -> Symbol:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if None in (left_type, right_type):
            raise SemanticError(
                "one of the node types are unkown", ErrorCode.UNKOWN_TYPE, node
            )
        match node.token.token_type:
            case (
                TokenType.MINUS
                | TokenType.FLOAT_DIV
                | TokenType.INTEGER_DIV
                | TokenType.MULTIPLICATION
            ):
                return self._bin_math(left_type, right_type)
            case TokenType.PLUS:
                return self._bin_string_concat(left_type, right_type)
            case (
                TokenType.MORE
                | TokenType.LESS
                | TokenType.MORE_OR_EQUAL
                | TokenType.LESS_OR_EQUAL
            ):
                return self._bin_compare(left_type, right_type, node.token.token_type)
            case TokenType.EQUAL | TokenType.NOT_EQUAL:
                return BuiltinTypes.BOOLEAN.value
            case TokenType.AND | TokenType.OR:
                return self._bin_bool(left_type, right_type, node.token.token_type)
        raise SemanticError(
            f"unkown binary operator {node.token}",
            ErrorCode.UNKOWN_BINARY_OPERATOR,
            node,
        )

    def _bin_bool(self, left: Symbol, right: Symbol, operator: TokenType) -> Symbol:
        if right == left == BuiltinTypes.BOOLEAN.value:
            return BuiltinTypes.BOOLEAN.value
        raise SemanticError(
            f"unsupported boolean operator {operator.value} between {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
        )

    def _bin_compare(self, left: Symbol, right: Symbol, operator: TokenType) -> Symbol:
        if left in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value):
            if right in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value):
                return BuiltinTypes.BOOLEAN.value
        raise SemanticError(
            f"unsupported {operator.value} compare operation for {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
        )

    def _bin_string_concat(self, left: Symbol, right: Symbol) -> Symbol:
        if left in (BuiltinTypes.CHAR.value, BuiltinTypes.STRING.value):
            if right in (BuiltinTypes.CHAR.value, BuiltinTypes.STRING.value):
                return BuiltinTypes.STRING.value
        return self._bin_math(left, right)

    def _bin_math(self, left: Symbol, right: Symbol) -> Symbol:
        if left in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value):
            if right in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value):
                return (
                    BuiltinTypes.REAL.value
                    if BuiltinTypes.REAL.value in (left, right)
                    else BuiltinTypes.INTEGER.value
                )
        raise SemanticError(
            f"unsupported + operation for {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
        )

    @override
    def visit_Param(self, node: Param) -> Symbol:
        type_symbol = self.get_current_scope().lookup(node.type_node.value)
        if type_symbol is None:
            raise SemanticError(
                f"unkown type {node.type_node.value}", ErrorCode.UNKOWN_TYPE, node
            )
        return type_symbol

    @override
    def visit_Call(self, node: Call[Symbol]) -> Symbol | None:
        callable_name = node.name
        callable_symbol = self.get_current_scope().lookup_callable(callable_name)
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
        if callable_symbol.return_type is not None:
            return callable_symbol.return_type
        return None

    @override
    def visit_IfStatement(self, node: IfStatement) -> Any:
        self.visit(node.main_condition)
        for other_cond in node.secondary_conditions:
            self.visit(other_cond)
        if node.else_condition:
            self.visit(node.else_condition)
        return None

    @override
    def visit_Condition(self, node: Condition) -> None:
        type_symbol = self.visit(node.condition)
        if type_symbol != BuiltinTypes.BOOLEAN.value:
            raise SemanticError(
                f"if expression should contain boolean, but {type_symbol} was provided",
                ErrorCode.INCORRECT_TYPE,
                node,
            )
        self.visit(node.expr)

    @override
    def visit_Str(self, node: Str) -> Symbol:
        return BuiltinTypes.STRING.value

    def analyze(self, tree: AST) -> AST:
        self.visit(tree)
        return tree
