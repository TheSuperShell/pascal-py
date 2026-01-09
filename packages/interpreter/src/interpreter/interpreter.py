from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, override
from parser import (
    Assign,
    Block,
    Compound,
    Num,
    Param,
    Parser,
    BinOp,
    Procedure,
    Call,
    Program,
    Type,
    UnaryOp,
    Var,
    VarDecl,
)
from interpreter.semantic_analyzer import SymbolTableVisitor
from parser.parser import (
    Bool,
    BuiltinCallableSymbol,
    Condition,
    Exit,
    Function,
    CallableSymbol,
    IfStatement,
)
from parser.token import TokenType
from interpreter.utils import ARType, ActivationRecord, CallStack
from interpreter.visitor import Visitor


class InterpreterError(Exception): ...


class ExitScope(Exception):
    def __init__(self, value: Any = None) -> None:
        self.value = value


_OPERATIONS: dict[TokenType, Callable[[Any, Any], Any]] = {
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
class DefaultVisitor(Visitor):
    call_stack: CallStack = field(default_factory=CallStack)

    @override
    def visit_Program(self, node: Program) -> Any:
        program_name = node.name

        ar = ActivationRecord(program_name, ARType.PROGRAM, 1)
        self.call_stack.push(ar)

        print(f"ENTER PROGRAM: {program_name}")
        print(self.call_stack)

        self.visit(node.block)

        print(f"LEAVE PROGRAM: {program_name}")
        print(self.call_stack)

        self.call_stack.pop()

    @override
    def visit_Block(self, node: Block) -> Any:
        for decl in node.declarations:
            self.visit(decl)
        return self.visit(node.compund_statement)

    @override
    def visit_Compound(self, node: Compound) -> Any:
        for child in node.children:
            self.visit(child)

    @override
    def visit_Procedure(self, node: Procedure) -> Any:
        return

    @override
    def visit_Function(self, node: Function) -> Any:
        return

    @override
    def visit_Param(self, node: Param) -> Any:
        return None

    @override
    def visit_Num(self, node: Num) -> Any:
        return node.value

    @override
    def visit_Bool(self, node: Bool) -> Any:
        return node.value

    @override
    def visit_Assign(self, node: Assign) -> Any:
        var_name = node.left.value
        self.call_stack.peek()[var_name] = self.visit(node.right)
        return None

    @override
    def visit_Var(self, node: Var) -> Any:
        var_name = node.value
        val = self.call_stack.lookup(var_name)
        if val is None:
            raise NameError(repr(var_name))
        return val

    @override
    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return _UNARY_OP[node.token.token_type](self.visit(node.expr))

    @override
    def visit_VarDecl(self, node: VarDecl) -> Any:
        return

    @override
    def visit_Type(self, node: Type) -> Any:
        return

    @override
    def visit_BinOp(self, node: BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        return _OPERATIONS[node.token.token_type](left, right)

    def _visit_builtin_callable(self, symbol: BuiltinCallableSymbol, node: Call) -> Any:
        inputs = []
        for param in node.actual_params:
            inputs.append(self.visit(param))
        print(f"CALL builtin: {symbol.name}")
        return symbol.func(*inputs)

    @override
    def visit_Call(self, node: Call) -> Any:
        proc_symbol = node.proc_symbol
        if proc_symbol is None:
            raise InterpreterError(f"{node.name} is not recognised")
        if isinstance(proc_symbol, BuiltinCallableSymbol):
            return self._visit_builtin_callable(proc_symbol, node)
        assert isinstance(proc_symbol, CallableSymbol)
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
        for param_symbol, actual_param in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(actual_param)

        self.call_stack.push(ar)

        print(f"ENTER PROCEDURE: {proc_name}")
        print(self.call_stack)

        result = None
        try:
            self.visit(proc_symbol.block_ast)
        except ExitScope as e:
            result = e.value
        if result is None:
            result = ar.get("result")

        print(f"LEAVE PROCEDURE: {proc_name}")
        print(self.call_stack)

        self.call_stack.pop()
        return result

    @override
    def visit_IfStatement(self, node: IfStatement) -> Any:
        if self.visit(node.main_condition):
            return
        for secondary in node.secondary_conditions:
            if self.visit(secondary):
                return
        if node.else_condition is None:
            return
        self.visit(node.else_condition)

    @override
    def visit_Condition(self, node: Condition) -> Any:
        result = self.visit(node.condition)
        if result:
            self.visit(node.expr)
        return result

    @override
    def visit_Exit(self, node: Exit) -> Any:
        print(f"EXIT {self.call_stack.peek().name}")
        result = None
        if node.expr is not None:
            result = self.visit(node.expr)
        raise ExitScope(result)


@dataclass(slots=True)
class Interpreter:
    parser: Parser
    semanti_analyzer: Visitor = field(default_factory=SymbolTableVisitor)
    default_visitor: Visitor = field(default_factory=DefaultVisitor)

    def process(self) -> Any:
        tree = self.parser.parse()
        self.semanti_analyzer.visit(tree)
        return self.default_visitor.visit(tree)
