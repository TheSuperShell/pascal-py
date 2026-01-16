from collections.abc import Callable
import contextlib
import logging
from interpreter.errors import InterpreterError
from dataclasses import dataclass, field
from typing import Any, override
from interpreter.symbols import (
    PythonTypes,
    RangedArraySymbol,
    BuiltinCallableSymbol,
    BuiltinInput,
    CustomCallableSymbol,
    ConstSymbol,
    DynamicArraySymbol,
    ParamMode,
    RangeSymbol,
    Ref,
    Symbol,
    TypeSymbol,
    VarRef,
    cast,
)
from parser import (
    Assign,
    Block,
    Compound,
    Param,
    BinOp,
    Procedure,
    Call,
    Program,
    UnaryOp,
    Var,
    VarDecl,
)
from parser.errors import ErrorCode
from parser.parser import (
    AST,
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
from parser.token import TokenType
from interpreter.utils import ARType, ActivationRecord, CallStack
from interpreter.visitor import Visitor


class ExitScope(Exception):
    def __init__(self, value: PythonTypes | None = None) -> None:
        self.value = value


class ContinueLoop(Exception): ...


class BreakLoop(Exception): ...


_OPERATIONS: dict[TokenType, Callable[[Any, Any], PythonTypes]] = {
    TokenType.PLUS: lambda x, y: x + y,
    TokenType.MINUS: lambda x, y: x - y,
    TokenType.MULTIPLICATION: lambda x, y: x * y,
    TokenType.INTEGER_DIV: lambda x, y: x // y,
    TokenType.FLOAT_DIV: lambda x, y: x / y,
    TokenType.LESS: lambda x, y: x < y,
    TokenType.MORE: lambda x, y: x > y,
    TokenType.LESS_OR_EQUAL: lambda x, y: x <= y,
    TokenType.MORE_OR_EQUAL: lambda x, y: x >= y,
    TokenType.EQUAL: lambda x, y: x == y,
    TokenType.NOT_EQUAL: lambda x, y: x != y,
    TokenType.AND: lambda x, y: x and y,
    TokenType.OR: lambda x, y: x or y,
}

_UNARY_OP: dict[TokenType, Callable[[Any], Any]] = {
    TokenType.PLUS: lambda x: x,
    TokenType.MINUS: lambda x: -x,
    TokenType.NOT: lambda x: not x,
}


@dataclass(slots=True)
class Interpreter(Visitor[PythonTypes]):
    logger: logging.Logger
    call_stack: CallStack = field(default_factory=CallStack)

    @override
    def visit_Program(self, node: Program[Symbol]) -> None:
        program_name = node.name

        ar = ActivationRecord(program_name, ARType.PROGRAM, 1)
        self.call_stack.push(ar)

        self.logger.debug(f"ENTER PROGRAM: {program_name}")
        self.logger.debug(self.call_stack)

        with contextlib.suppress(ExitScope):
            self.visit(node.block)

        self.logger.debug(f"LEAVE PROGRAM: {program_name}")
        self.logger.debug(self.call_stack)

        self.call_stack.pop()

    @override
    def visit_Block(self, node: Block[Symbol]) -> None:
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compund_statement)

    @override
    def visit_Compound(self, node: Compound[Symbol]) -> None:
        for child in node.children:
            self.visit(child)

    @override
    def visit_Procedure(self, node: Procedure[Symbol]) -> None:
        return

    @override
    def visit_Function(self, node: Function[Symbol]) -> None:
        return

    @override
    def visit_Param(self, node: Param[Symbol]) -> PythonTypes:
        return 0

    @override
    def visit_Literal(self, node: Literal[PythonTypes, Symbol]) -> PythonTypes:
        return node.value

    @override
    def visit_Assign(self, node: Assign[Symbol]) -> None:
        var_name = node.left.value
        var_value = self.visit_not_none(node.right)
        var_type = node.left.type_symbol
        if isinstance(var_type, RangeSymbol):
            assert var_type.ordinal_rank and var_type.ordinal_value
            var_value_ord = var_type.ordinal_rank(var_value)
            if var_value_ord < var_type.min_value or var_value_ord > var_type.max_value:
                raise InterpreterError(
                    f"the value {var_value} is outside of the range bounds {var_type}",
                    ErrorCode.RANGE_OUT_OF_BOUNDS,
                )
        self.call_stack.peek()[var_name].set(var_value)
        return None

    @override
    def visit_Var(self, node: Var[Symbol]) -> PythonTypes:
        var_name = node.value
        if isinstance(node.symbol, ConstSymbol):
            return node.symbol.value
        val = self.call_stack.lookup_value(var_name)
        if val is None:
            raise InterpreterError(
                f"unkown variable {var_name} or the variable is not set",
                ErrorCode.UNASSIGNED_VARIABLE,
            )
        return val

    @override
    def visit_UnaryOp(self, node: UnaryOp[Symbol]) -> PythonTypes:
        value = self.visit_not_none(node.expr)
        return _UNARY_OP[node.token.token_type](value)

    @override
    def visit_VarDecl(self, node: VarDecl[Symbol]) -> None:
        var_ref = VarRef[PythonTypes](node.var_node.value)
        if node.default_value is not None:
            var_ref.set(node.default_value.value)
        elif isinstance(node.var_node.type_symbol, RangedArraySymbol):
            array_type = node.var_node.type_symbol
            array = self._array_init(array_type)
            var_ref.set(array)
        self.call_stack.peek()[node.var_node.value] = var_ref

    def _array_init(self, type_symbol: RangedArraySymbol) -> list[PythonTypes | None]:
        index_type = type_symbol.index_type
        assert isinstance(index_type, RangeSymbol)
        length = index_type.max_value - index_type.min_value
        if not isinstance(type_symbol.element_type, RangedArraySymbol):
            return [None for _ in range(length)]
        return [self._array_init(type_symbol.element_type) for _ in range(length)]

    @override
    def visit_StandardType(self, node: StandardType[Symbol]) -> PythonTypes:
        return 0

    @override
    def visit_BinOp(self, node: BinOp[Symbol]) -> PythonTypes:
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _OPERATIONS[node.token.token_type](left, right)

    def _visit_ref(self, node: AST[Symbol]) -> Ref[PythonTypes]:
        assert isinstance(node, Var)
        variable = self.call_stack.lookup(node.value)
        if variable is None:
            raise InterpreterError(f"variable {node.value} reference does not exist")
        return variable

    def _visit_builtin_callable(
        self, symbol: BuiltinCallableSymbol[PythonTypes], node: Call[Symbol]
    ) -> PythonTypes | None:
        inputs: BuiltinInput = []
        for i, param in enumerate(node.actual_params):
            mode_ind = i  # if symbol.params else 0
            mode = (
                symbol.param_modes[mode_ind]
                if i < len(symbol.param_modes)
                else symbol.param_modes[0]
            )
            val = (
                self.visit_not_none(param)
                if mode == ParamMode.VALUE
                else self._visit_ref(param)
            )
            assert isinstance(param.type_symbol, TypeSymbol)
            inputs.append((val, param.type_symbol))
        self.logger.debug(f"CALL builtin: {symbol.name}")
        return symbol.func(inputs)

    @override
    def visit_Call(self, node: Call[Symbol]) -> PythonTypes | None:
        proc_symbol = node.proc_symbol
        if proc_symbol is None:
            raise InterpreterError(f"{node.name} is not recognised")
        if isinstance(proc_symbol, BuiltinCallableSymbol):
            return self._visit_builtin_callable(proc_symbol, node)
        assert isinstance(proc_symbol, CustomCallableSymbol)
        if proc_symbol.block_ast is None:
            raise InterpreterError(f"{node.name} body is not declared")
        proc_name = node.name

        ar = ActivationRecord(
            proc_name,
            ARType.FUNCTION if proc_symbol.return_type else ARType.PROCEDURE,
            nesting_level=proc_symbol.scope + 1,
        )
        formal_params = proc_symbol.params
        actual_params = node.actual_params
        assert formal_params is not None
        for param_symbol, param_mode, actual_param in zip(
            formal_params, proc_symbol.param_modes, actual_params
        ):
            param_type = param_symbol.symbol_type
            if param_mode == ParamMode.VALUE:
                input_value = self.visit_not_none(actual_param)
                var_ref = VarRef(param_symbol.name, input_value)
                if isinstance(param_type, RangeSymbol):
                    assert param_type.ordinal_rank
                    var_value_ord = param_type.ordinal_rank(input_value)
                    if (
                        var_value_ord < param_type.min_value
                        or var_value_ord > param_type.max_value
                    ):
                        raise InterpreterError(
                            f"the value {input_value} is outside of the range bounds {param_type}",
                            ErrorCode.RANGE_OUT_OF_BOUNDS,
                        )
            else:
                assert isinstance(actual_param, Var)
                var_ref = self.call_stack.lookup(actual_param.value)
                assert var_ref is not None
            ar[param_symbol.name] = var_ref

        ar["result"] = VarRef[PythonTypes]("result")
        ar[node.name] = VarRef[PythonTypes](node.name)

        self.call_stack.push(ar)

        self.logger.debug(f"ENTER PROCEDURE: {proc_name}")
        self.logger.debug(self.call_stack)

        result = None
        try:
            self.visit(proc_symbol.block_ast)
        except ExitScope as e:
            result = e.value
        if result is None:
            result = ar.get_value("result")
        if result is None:
            result = ar.get_value(proc_name)

        self.logger.debug(f"LEAVE PROCEDURE: {proc_name}")
        self.logger.debug(self.call_stack)

        self.call_stack.pop()
        return result

    @override
    def visit_IfStatement(self, node: IfStatement[Symbol]) -> None:
        if self._visit_condition(node.main_condition):
            return
        for secondary in node.secondary_conditions:
            if self._visit_condition(secondary):
                return
        if node.else_condition is None:
            return
        self.visit(node.else_condition)

    def _visit_condition(self, node: Condition[Symbol]) -> bool:
        result = self.visit(node.condition)
        if result:
            self.visit(node.expr)
        assert result is bool
        return result

    @override
    def visit_Condition(self, node: Condition[Symbol]) -> None:
        return

    @override
    def visit_Exit(self, node: Exit[Symbol]) -> None:
        self.logger.debug(f"EXIT {self.call_stack.peek().name}")
        result = None
        if node.expr is not None:
            result = self.visit(node.expr)
        raise ExitScope(result)

    @override
    def visit_WhileStatement(self, node: WhileStatement[Symbol]) -> None:
        with contextlib.suppress(BreakLoop):
            while self.visit(node.condition):
                with contextlib.suppress(ContinueLoop):
                    self.visit(node.expr)

    @override
    def visit_ForInStatement(self, node: ForInStatement[Symbol]) -> None:
        range_type_symbol = node.range_expr.type_symbol
        assert isinstance(range_type_symbol, RangeSymbol)
        assert range_type_symbol.ordinal_value
        with contextlib.suppress(BreakLoop):
            for i in range(range_type_symbol.min_value, range_type_symbol.max_value):
                self.call_stack.peek()[node.var.value].set(
                    range_type_symbol.ordinal_value(i)
                )
                with contextlib.suppress(ContinueLoop):
                    self.visit(node.expr)

    @override
    def visit_ForStatement(self, node: ForStatement[Symbol]) -> None:
        init_state_ts = node.init_state.type_symbol
        end_state_ts = node.end_state.type_symbol
        assert isinstance(init_state_ts, TypeSymbol) and isinstance(
            end_state_ts, TypeSymbol
        )
        assert (
            init_state_ts.ordinal_rank
            and init_state_ts.ordinal_value
            and end_state_ts.ordinal_rank
        )
        init_state = self.visit_not_none(node.init_state)
        self.call_stack.peek()[node.var.value].set(init_state)
        end_state = self.visit(node.end_state)
        end_state_ord: int = end_state_ts.ordinal_rank(end_state)
        current_state_ord: int = init_state_ts.ordinal_rank(init_state)
        with contextlib.suppress(BreakLoop):
            while current_state_ord < end_state_ord:
                with contextlib.suppress(ContinueLoop):
                    self.visit(node.expr)
                current_state_ord += 1
                self.call_stack.peek()[node.var.value].set(
                    init_state_ts.ordinal_value(current_state_ord)
                )

    @override
    def visit_Break(self, node: Break) -> None:
        raise BreakLoop()

    @override
    def visit_Continue(self, node: Continue) -> None:
        raise ContinueLoop()

    @override
    def visit_TypeDecl(self, node: TypeDecl[Symbol]) -> None:
        return

    @override
    def visit_ConstDecl(self, node: ConstDecl[Symbol]) -> None:
        return

    @override
    def visit_Range(self, node: Range[Symbol]) -> PythonTypes:
        return 0

    @override
    def visit_Array(self, node: Array[Symbol]) -> PythonTypes:
        return 0

    @override
    def visit_DynamicArray(self, node: DynamicArray[Symbol]) -> PythonTypes:
        return 0

    @override
    def visit_Enum(self, node: Enum[Symbol]) -> PythonTypes:
        for i, item in enumerate(node.items):
            self.call_stack.peek()[item.value].set(i)
        return 0

    @override
    def visit_IndexOf(self, node: IndexOf[Symbol]) -> PythonTypes:
        array = self.visit_not_none(node.var_node)
        assert isinstance(array, list)
        array_type = node.var_node.type_symbol
        assert isinstance(array_type, RangedArraySymbol)
        index_value = array_type.get_index_from_index_value(
            self.visit(node.index_value)
        )
        if index_value < 0 or index_value >= len(array):
            raise InterpreterError("index our of range", ErrorCode.INDEX_OUT_OF_RANGE)
        val = array[index_value]
        for ind in node.other_indicies:
            array_type = array_type.element_type
            assert isinstance(array_type, RangedArraySymbol)
            index_value = array_type.get_index_from_index_value(self.visit(ind))
            if index_value < 0 or index_value >= len(array):
                raise InterpreterError(
                    "index our of range", ErrorCode.INDEX_OUT_OF_RANGE
                )
            assert isinstance(val, list)
            val = val[index_value]
        if val is None:
            raise InterpreterError("array value is not assigned")
        return val

    @override
    def visit_AssignIndex(self, node: AssignIndex[Symbol]) -> None:
        value = self.visit(node.right)
        array = self.visit_not_none(node.left.var_node)
        assert isinstance(array, list)
        array_type = node.left.var_node.type_symbol
        assert isinstance(array_type, RangedArraySymbol) or isinstance(
            array_type, DynamicArraySymbol
        )
        index_value = array_type.get_index_from_index_value(
            cast(self.visit_not_none(node.left.index_value), int)
        )
        if index_value < 0 or index_value >= len(array):
            raise InterpreterError(
                f"index our of range: {index_value}", ErrorCode.INDEX_OUT_OF_RANGE
            )
        for ind in node.left.other_indicies:
            array = array[index_value]
            assert isinstance(array, list)
            array_type = array_type.element_type
            assert isinstance(array_type, RangedArraySymbol)
            index_value = array_type.get_index_from_index_value(self.visit(ind))
            if index_value < 0 or index_value >= len(array):
                raise InterpreterError(
                    f"index our of range: {index_value}", ErrorCode.INDEX_OUT_OF_RANGE
                )
        array[index_value] = value

    def interpret(self, tree: AST) -> AST:
        self.visit(tree)
        return tree
