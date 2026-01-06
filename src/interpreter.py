from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, override
from src.parser import (
    Assign,
    Block,
    Compound,
    Num,
    Param,
    Parser,
    BinOp,
    Procedure,
    ProcedureCall,
    ProcedureSymbol,
    Program,
    Type,
    UnaryOp,
    Var,
    VarDecl,
)
from src.semantic_analyzer import SymbolTableVisitor
from src.token import TokenType
from src.utils import ARType, ActivationRecord, CallStack
from src.visitor import Visitor


class InterpreterError(Exception): ...


_OPERATIONS: dict[TokenType, Callable[[int | float, int | float], int | float]] = {
    TokenType.PLUS: lambda x, y: x + y,
    TokenType.MINUS: lambda x, y: x - y,
    TokenType.MULTIPLICATION: lambda x, y: x * y,
    TokenType.INTEGER_DIV: lambda x, y: x // y,
    TokenType.FLOAT_DIV: lambda x, y: x / y,
}

_UNARY_OP: dict[TokenType, Callable[[int | float], int | float]] = {
    TokenType.PLUS: lambda x: x,
    TokenType.MINUS: lambda x: -x,
}


@dataclass(slots=True)
class DefaultVisitor(Visitor):
    call_stack: CallStack[ActivationRecord] = field(default_factory=CallStack)

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
    def visit_Param(self, node: Param) -> Any:
        return None

    @override
    def visit_Num(self, node: Num) -> Any:
        return node.value

    @override
    def visit_Assign(self, node: Assign) -> Any:
        var_name = node.left.value
        self.call_stack.peek()[var_name] = self.visit(node.right)
        return None

    @override
    def visit_Var(self, node: Var) -> Any:
        var_name = node.value
        val = self.call_stack.peek().get(var_name)
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

    @override
    def visit_ProcedureCall(self, node: ProcedureCall) -> Any:
        proc_symbol = node.proc_symbol
        if proc_symbol is None:
            raise InterpreterError(f"procdure {node.proc_name} is not recognised")
        assert isinstance(proc_symbol, ProcedureSymbol)
        if proc_symbol.block_ast is None:
            raise InterpreterError(f"procedure's {node.proc_name} body is not declared")
        proc_name = node.proc_name

        ar = ActivationRecord(proc_name, ARType.PROCEDURE, nesting_level=2)
        formal_params = proc_symbol.params
        actual_params = node.actual_params
        for param_symbol, actual_param in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(actual_param)

        self.call_stack.push(ar)

        print(f"ENTER PROCEDURE: {proc_name}")
        print(self.call_stack)

        self.visit(proc_symbol.block_ast)

        print(f"LEAVE PROCEDURE: {proc_name}")
        print(self.call_stack)

        self.call_stack.pop()


@dataclass(slots=True)
class Interpreter:
    parser: Parser
    semanti_analyzer: Visitor = field(default_factory=SymbolTableVisitor)
    default_visitor: Visitor = field(default_factory=DefaultVisitor)

    def process(self) -> Any:
        tree = self.parser.parse()
        self.semanti_analyzer.visit(tree)
        return self.default_visitor.visit(tree)
