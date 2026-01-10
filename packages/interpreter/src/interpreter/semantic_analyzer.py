from dataclasses import dataclass
import logging
from typing import Any, Self, override

from interpreter.builtins import BuiltinTypes
from interpreter.errors import SemanticError
from interpreter.symbols import (
    BuiltinCallableSymbol,
    CallableSymbol,
    ProgramSymbol,
    RangeSymbol,
    Symbol,
    TypeSymbol,
    VarSymbol,
)
from interpreter.utils import ScopeType, ScopedSymbolTable
from parser import (
    Assign,
    BinOp,
    Block,
    Compound,
    Param,
    Procedure,
    Call,
    Program,
    UnaryOp,
    Var,
    VarDecl,
)
from interpreter.visitor import Visitor
from parser.errors import ErrorCode
from parser.parser import (
    AST,
    Break,
    Condition,
    ConstDecl,
    Continue,
    Exit,
    ForStatement,
    Function,
    IfStatement,
    Literal,
    Range,
    TypeDecl,
    WhileStatement,
    StandardType,
)
from parser.token import Token, TokenType


@dataclass(slots=True)
class SymbolTableVisitor(Visitor):
    logger: logging.Logger
    current_scope: ScopedSymbolTable | None = None
    loop_depth: int = 0

    @classmethod
    def new(cls, logger: logging.Logger) -> Self:
        return cls(logger, ScopedSymbolTable.create_builtin_scope(logger))

    def get_current_scope(self) -> ScopedSymbolTable:
        assert self.current_scope
        return self.current_scope

    @override
    def visit_Program(self, node: Program) -> None:
        program_name = node.name
        self.get_current_scope().define(ProgramSymbol(program_name, 0))
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
    def visit_Block(self, node: Block) -> None:
        for decls in node.declarations:
            self.visit(decls)
        self.visit(node.compund_statement)

    @override
    def visit_Exit(self, node: Exit) -> None:
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
    def visit_Compound(self, node: Compound) -> None:
        for child in node.children:
            self.visit(child)

    @override
    def visit_Function(self, node: Function) -> None:
        func_name = node.name
        return_symbol = self.visit(node.return_type)
        func_symbol = CallableSymbol(func_name, 0, return_type=return_symbol)
        self.get_current_scope().define(func_symbol)

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
            param_type = self.visit(param)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, 0, param_type)
            self.current_scope.define(var_symbol)
            func_symbol.params.append(var_symbol)

        result_exists = self.current_scope.lookup_variable(
            "result", current_scope_only=True
        )
        func_var_exists = self.current_scope.lookup_variable(
            func_name, current_scope_only=True
        )
        if result_exists is not None or func_var_exists is not None:
            raise SemanticError(
                f"result and {func_name} are special symbols and cannot be overridden: {result_exists=}, {func_var_exists=}",
                ErrorCode.DUPLICATE_VARIABLE,
                node,
            )
        self.current_scope.define(VarSymbol("result", 0, return_symbol))
        self.current_scope.define(VarSymbol(func_name, 0, return_symbol))

        self.visit(node.block)
        self.logger.debug(function_scope)
        self.current_scope = self.get_current_scope().enclosing_scope
        self.logger.debug(f"LEAVE scope: {func_name}")

        func_symbol.block_ast = node.block

    @override
    def visit_Procedure(self, node: Procedure) -> None:
        proc_name = node.name
        proc_symbol = CallableSymbol(proc_name, 0)
        self.get_current_scope().define(proc_symbol)

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
            param_type = self.visit(param)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, 0, param_type)
            self.current_scope.define(var_symbol)
            proc_symbol.params.append(var_symbol)

        self.visit(node.block)
        self.logger.debug(procedure_scope)
        self.current_scope = self.current_scope.enclosing_scope
        self.logger.debug(f"LEAVE scope: {proc_name}")

        proc_symbol.block_ast = node.block

    @override
    def visit_Literal(self, node: Literal[Any, Symbol]) -> TypeSymbol:
        type_symbol = BuiltinTypes.literal_to_builtin(node).value
        node.type_symbol = type_symbol
        return type_symbol

    @override
    def visit_Assign(self, node: Assign) -> None:
        var_symbol = self.get_current_scope().lookup_variable(node.left.value)
        if var_symbol is None:
            raise SemanticError(
                f"unkown variable {node.left.value}", ErrorCode.ID_NOT_FOUND, node
            )
        if var_symbol.const:
            raise SemanticError(
                f"cannot assign to a const value {var_symbol}",
                ErrorCode.ASSIGN_TO_CONST,
                node,
            )
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if right_type is None:
            raise SemanticError(
                f"type of {node.right} in assignment is unkown",
                ErrorCode.UNKOWN_TYPE,
                node,
            )
        if left_type == right_type:
            return
        if left_type == BuiltinTypes.REAL.value and right_type in (
            BuiltinTypes.REAL.value,
            BuiltinTypes.INTEGER.value,
        ):
            return
        if left_type == BuiltinTypes.STRING and right_type in (
            BuiltinTypes.STRING,
            BuiltinTypes.CHAR,
        ):
            return
        raise SemanticError(
            f"cannot assing {node.right} of type {right_type} to variable {node.left} of type {left_type}",
            ErrorCode.UNASSIGNABLE_TYPES,
        )

    @override
    def visit_Var(self, node: Var) -> TypeSymbol:
        var_name = node.value
        var_symbol = self.get_current_scope().lookup_variable(var_name)
        if var_symbol is None:
            raise SemanticError(
                f"symbol not found {var_name}", ErrorCode.ID_NOT_FOUND, node
            )
        node.type_symbol = var_symbol.symbol_type
        return var_symbol.symbol_type

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> TypeSymbol:
        type_symbol = self.visit(node.expr)
        node.type_symbol = type_symbol
        return type_symbol

    @override
    def visit_VarDecl(self, node: VarDecl) -> None:
        type_symbol = self.visit(node.type_node)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, 0, type_symbol)
        node.var_node.type_symbol = type_symbol

        if (
            self.get_current_scope().lookup_variable(var_name, current_scope_only=True)
            is not None
        ):
            raise SemanticError(
                f"duplicate identifier {var_name} found",
                ErrorCode.DUPLICATE_VARIABLE,
                node,
            )
        self.get_current_scope().define(var_symbol)
        if node.default_value is not None:
            self.visit_Assign(Assign(node.var_node, Token.assign(), node.default_value))

    @override
    def visit_StandardType(self, node: StandardType) -> TypeSymbol:
        type_symbol = self.get_current_scope().lookup_type(node.value)
        if type_symbol is None:
            raise SemanticError(
                f"unkown type {node.value}", ErrorCode.UNKOWN_TYPE, node
            )
        return type_symbol

    @override
    def visit_Range(self, node: Range[Symbol]) -> TypeSymbol:
        start_val_type_symbol = BuiltinTypes.literal_to_builtin(node.start_val).value
        end_val_type_symbol = BuiltinTypes.literal_to_builtin(node.end_val).value
        if start_val_type_symbol != end_val_type_symbol:
            raise SemanticError(
                "start and end types of a range should be the same, "
                f"got {start_val_type_symbol}, {end_val_type_symbol}",
                ErrorCode.INCORRECT_TYPE,
                node,
            )
        if (
            not start_val_type_symbol.is_ordinal
            or start_val_type_symbol.ordinal_rank is None
        ):
            raise SemanticError(
                f"range can only be created from enumerable values, got {start_val_type_symbol}",
                ErrorCode.INCORRECT_TYPE,
                node,
            )
        min_value = start_val_type_symbol.ordinal_rank(node.start_val.value)
        max_value = start_val_type_symbol.ordinal_rank(node.end_val.value)
        if min_value >= max_value:
            raise SemanticError()
        type_symbol = RangeSymbol[Any](
            node.value,
            0,
            start_val_type_symbol.f_type,
            start_val_type_symbol.ordinal_rank,
            start_val_type_symbol.ordinal_value,
            min_value,
            max_value,
        )
        self.get_current_scope().define(type_symbol)
        return type_symbol

    @override
    def visit_BinOp(self, node: BinOp) -> TypeSymbol:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if left_type is None or right_type is None:
            raise SemanticError(
                "one of the node types are unkown", ErrorCode.UNKOWN_TYPE, node
            )
        match node.token.token_type:
            case TokenType.MINUS | TokenType.FLOAT_DIV | TokenType.MULTIPLICATION:
                return self._bin_math(left_type, right_type, node)
            case TokenType.INTEGER_DIV:
                return self._bin_integer_div(left_type, right_type, node)
            case TokenType.PLUS:
                return self._bin_string_concat(left_type, right_type, node)
            case (
                TokenType.MORE
                | TokenType.LESS
                | TokenType.MORE_OR_EQUAL
                | TokenType.LESS_OR_EQUAL
            ):
                return self._bin_compare(
                    left_type, right_type, node.token.token_type, node
                )
            case TokenType.EQUAL | TokenType.NOT_EQUAL:
                return BuiltinTypes.BOOLEAN.value
            case TokenType.AND | TokenType.OR:
                return self._bin_bool(
                    left_type, right_type, node.token.token_type, node
                )
        raise SemanticError(
            f"unkown binary operator {node.token}",
            ErrorCode.UNKOWN_BINARY_OPERATOR,
            node,
        )

    def _bin_integer_div(self, left: Symbol, right: Symbol, node: BinOp) -> TypeSymbol:
        if left in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value) and right in (
            BuiltinTypes.INTEGER.value,
            BuiltinTypes.REAL.value,
        ):
            node.type_symbol = BuiltinTypes.INTEGER.value
            return BuiltinTypes.INTEGER.value
        raise SemanticError(
            f"unsupported integer division for {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
            node,
        )

    def _bin_bool(
        self, left: Symbol, right: Symbol, operator: TokenType, node: BinOp
    ) -> TypeSymbol:
        if right == left == BuiltinTypes.BOOLEAN.value:
            type_symbol = BuiltinTypes.BOOLEAN.value
            node.type_symbol = type_symbol
            return type_symbol
        raise SemanticError(
            f"unsupported boolean operator {operator.value} between {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
            node,
        )

    def _bin_compare(
        self, left: Symbol, right: Symbol, operator: TokenType, node: BinOp
    ) -> TypeSymbol:
        if left in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value) and right in (
            BuiltinTypes.INTEGER.value,
            BuiltinTypes.REAL.value,
        ):
            type_symbol = BuiltinTypes.BOOLEAN.value
            node.type_symbol = type_symbol
            return type_symbol
        raise SemanticError(
            f"unsupported {operator.value} compare operation for {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
            node,
        )

    def _bin_string_concat(
        self, left: Symbol, right: Symbol, node: BinOp
    ) -> TypeSymbol:
        if left in (BuiltinTypes.CHAR.value, BuiltinTypes.STRING.value) and right in (
            BuiltinTypes.CHAR.value,
            BuiltinTypes.STRING.value,
        ):
            type_symbol = BuiltinTypes.STRING.value
            node.type_symbol = type_symbol
            return type_symbol
        return self._bin_math(left, right, node)

    def _bin_math(self, left: Symbol, right: Symbol, node: BinOp) -> TypeSymbol:
        if left in (BuiltinTypes.INTEGER.value, BuiltinTypes.REAL.value) and right in (
            BuiltinTypes.INTEGER.value,
            BuiltinTypes.REAL.value,
        ):
            type_symbol = (
                BuiltinTypes.REAL.value
                if BuiltinTypes.REAL.value in (left, right)
                else BuiltinTypes.INTEGER.value
            )
            node.type_symbol = type_symbol
            return type_symbol
        raise SemanticError(
            f"unsupported + operation for {left} and {right}",
            ErrorCode.UNSUPPORTED_BINARY_OPERATION,
            node,
        )

    @override
    def visit_Param(self, node: Param) -> Symbol:
        type_symbol = self.visit(node.type_node)
        node.type_symbol = type_symbol
        return type_symbol

    @override
    def visit_Call(self, node: Call[Symbol]) -> TypeSymbol | None:
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
        if callable_symbol.params is not None:
            for i, param_node in enumerate(node.actual_params):
                param_type = self.visit(param_node)
                expected_type = callable_symbol.params[i].symbol_type
                if param_type is None:
                    raise SemanticError(
                        f"unkown function input type {param_node}",
                        ErrorCode.UNKOWN_TYPE,
                        node,
                    )
                if param_type != expected_type:
                    raise SemanticError(
                        f"incorrect callable {callable_name} input type for value {param_node}: "
                        f"expected {expected_type} got {param_type}",
                        ErrorCode.INCORRECT_INPUT_TYPE,
                        node,
                    )
        else:
            for param in node.actual_params:
                self.visit(param)
        if callable_symbol.return_type is not None:
            node.type_symbol = callable_symbol.return_type
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
    def visit_WhileStatement(self, node: WhileStatement) -> None:
        type_symbol = self.visit(node.condition)
        if type_symbol != BuiltinTypes.BOOLEAN.value:
            raise SemanticError(
                f"while condition should contain boolean, but {type_symbol} was provided",
                ErrorCode.INCORRECT_TYPE,
                node,
            )
        self.loop_depth += 1
        self.visit(node.expr)
        self.loop_depth -= 1

    @override
    def visit_ForStatement(self, node: ForStatement) -> None:
        var_symbol = self.get_current_scope().lookup_variable(node.var.value)
        init_state_type = self.visit(node.init_state)
        end_state_type = self.visit(node.end_state)
        if var_symbol is None:
            raise SemanticError(
                f"unkown variable in if statement {node.var}",
                ErrorCode.ID_NOT_FOUND,
                node,
            )
        if not isinstance(init_state_type, TypeSymbol) or not isinstance(
            end_state_type, TypeSymbol
        ):
            raise SemanticError("unkown init or end types", ErrorCode.UNKOWN_TYPE, node)
        if init_state_type != end_state_type:
            raise SemanticError(
                f"init state and end state should have the same type, got {init_state_type} and {end_state_type}",
                ErrorCode.INCORRECT_TYPE,
                node,
            )
        if not init_state_type.is_ordinal:
            raise SemanticError(
                f"if init and end states should be enumerable, got {init_state_type}",
                ErrorCode.INCORRECT_TYPE,
                node,
            )
        if init_state_type != var_symbol.symbol_type:
            raise SemanticError(
                f"cannot assign {init_state_type} to {var_symbol}",
                ErrorCode.UNASSIGNABLE_TYPES,
                node,
            )
        self.loop_depth += 1
        self.visit(node.expr)
        self.loop_depth -= 1

    @override
    def visit_Break(self, node: Break) -> None:
        if self.loop_depth <= 0:
            raise SemanticError(
                "break should be within loop", ErrorCode.OUTSIDE_LOOP, node
            )

    @override
    def visit_Continue(self, node: Continue) -> None:
        if self.loop_depth <= 0:
            raise SemanticError(
                "continue should be within loop", ErrorCode.OUTSIDE_LOOP, node
            )

    @override
    def visit_TypeDecl(self, node: TypeDecl[Symbol]) -> None:
        type_symbol = self.visit(node.type_node)
        if isinstance(type_symbol, RangeSymbol):
            self.get_current_scope().define(
                RangeSymbol(
                    node.var_node.value,
                    0,
                    type_symbol.f_type,
                    type_symbol.ordinal_rank,
                    type_symbol.ordinal_value,
                    type_symbol.min_value,
                    type_symbol.max_value,
                )
            )
            return
        self.get_current_scope().define(
            TypeSymbol(
                node.var_node.value,
                0,
                type_symbol.f_type,
                type_symbol.ordinal_rank,
                type_symbol.ordinal_value,
            )
        )

    @override
    def visit_ConstDecl(self, node: ConstDecl[Symbol]) -> None:
        var_name = node.var_node.value
        var_symbol = self.get_current_scope().lookup_variable(
            var_name, current_scope_only=True
        )
        if var_symbol is not None:
            raise SemanticError(
                f"duplicate identifier {var_name}", ErrorCode.DUPLICATE_VARIABLE, node
            )
        value = node.literal
        value_type = BuiltinTypes.literal_to_builtin(value).value
        self.get_current_scope().define(VarSymbol(var_name, 0, value_type, True))

    def analyze(self, tree: AST) -> AST:
        self.visit(tree)
        return tree
