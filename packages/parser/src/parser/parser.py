from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum, auto

from parser.lexer import Lexer

from parser.token import Token, TokenType


class ErrorCode(IntEnum):
    UNEXPECTED_TOKEN = auto()
    EOF_NOT_FOUND = auto()
    UNASSIGNED_VARIABLE = auto()


class ParserError(Exception):
    def __init__(
        self,
        message: str | None = None,
        error_code: ErrorCode | None = None,
        token: Token | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.token = token


class AST(ABC):
    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __str__(self) -> str: ...


@dataclass(slots=True, frozen=True)
class BinOp(AST):
    left: AST
    token: Token
    right: AST

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinOp):
            return False
        return (
            self.left == other.left
            and self.token == other.token
            and self.right == other.right
        )

    def __repr__(self) -> str:
        return f"BinOp(\n\tleft={self.left},\n\top={self.token},\n\tright={self.right})"

    def __str__(self) -> str:
        return f"{self.left}{self.token.value}{self.right}"


@dataclass(slots=True, frozen=True)
class Num(AST):
    token: Token

    @property
    def value(self) -> int | float:
        return (
            int(self.token.value)
            if self.token.token_type == TokenType.INTEGER_CONST
            else float(self.token.value)
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Num):
            return False
        return self.value == other.value

    def __repr__(self) -> str:
        return f"Num({self.value})"

    def __str__(self) -> str:
        return f"{self.value}"


@dataclass(slots=True, frozen=True)
class UnaryOp(AST):
    token: Token
    expr: AST

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnaryOp):
            return False
        return self.expr == other.expr and self.token == other.token

    def __repr__(self) -> str:
        return f"UnaryOp(\n\top={self.token},\n\texpr={self.expr}\n)"

    def __str__(self) -> str:
        return f"{self.token.value}{str(self.expr)}"


@dataclass(slots=True, frozen=True)
class Compound(AST):
    children: tuple[AST, ...]

    def __str__(self) -> str:
        children = "\n".join([str(c) for c in self.children])
        return f"BEGIN\n{children}\nEND"

    def __repr__(self) -> str:
        return f"Compund({self.children})"


@dataclass(slots=True, frozen=True)
class Assign(AST):
    left: "Var"
    token: Token
    right: AST

    def __str__(self) -> str:
        return f"{self.left}:={self.right}"

    def __repr__(self) -> str:
        return f"Assign(left={self.left}, right={self.right})"


@dataclass(slots=True, frozen=True)
class Var(AST):
    token: Token

    @property
    def value(self) -> str:
        return self.token.value

    def __repr__(self) -> str:
        return f"Var({self.value})"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NoOp(AST):
    def __str__(self) -> str:
        return "\\N"

    def __repr__(self) -> str:
        return "NoOp()"


@dataclass(frozen=True, slots=True)
class Program(AST):
    name: str
    block: "Block"

    def __str__(self) -> str:
        return f"-- {self.name} --\n"

    def __repr__(self) -> str:
        return f"Program(name={self.name}, block={self.block})"


@dataclass(frozen=True, slots=True)
class Block(AST):
    declarations: "tuple[VarDecl | Procedure | Function, ...]"
    compund_statement: Compound

    def __str__(self) -> str:
        return str(self.compund_statement)

    def __repr__(self) -> str:
        return f"Block({self.declarations=}, {self.compund_statement=})"


@dataclass(frozen=True, slots=True)
class VarDecl(AST):
    var_node: Var
    type_node: "Type"

    def __str__(self) -> str:
        return f"{self.var_node}: {self.type_node}"

    def __repr__(self) -> str:
        return f"VarDecl({self.var_node}:{self.type_node})"


@dataclass(frozen=True, slots=True)
class Type(AST):
    token: Token

    @property
    def value(self) -> str:
        return self.token.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Procedure(AST):
    name: str
    block: Block
    params: "tuple[Param, ...]"

    def __str__(self) -> str:
        params = ", ".join(str(param) for param in self.params)
        return f"{self.name}({params}):\n{self.block}"

    def __repr__(self) -> str:
        return f"Procedure({self.name=}, {self.params=}, {self.block=})"


@dataclass(frozen=True, slots=True)
class Function(AST):
    name: str
    block: Block
    params: "tuple[Param, ...]"
    return_type: Type

    def __str__(self) -> str:
        params = ", ".join(str(param) for param in self.params)
        return f"{self.name}({params}): {self.return_type}"

    def __repr__(self) -> str:
        return f"Function({self.name=}, {self.params=}, {self.return_type=}, {self.block=})"


@dataclass(frozen=True, slots=True)
class Param(AST):
    var_node: Var
    type_node: Type

    def __str__(self) -> str:
        return f"{self.var_node}: {self.type_node}"

    def __repr__(self) -> str:
        return f"Param({self.var_node=}, {self.type_node})"


@dataclass(slots=True)
class ProcedureCall(AST):
    proc_name: str
    actual_params: tuple[AST, ...]
    token: Token
    proc_symbol: "Symbol | None" = None

    def __str__(self) -> str:
        return f"{self.proc_name}({self.actual_params})"

    def __repr__(self) -> str:
        return f"ProcedureCall({self.proc_name=}, {self.actual_params=})"


@dataclass(slots=True, frozen=True)
class Exit(AST):
    expr: None | AST = None

    def __str__(self) -> str:
        return "Exit" + (f": {self.expr}" if self.expr else "")

    def __repr__(self) -> str:
        return f"Exit({self.expr=})"


class Symbol(ABC):
    __slots__ = "name", "symbol_type", "scope"

    def __init__(self, name: str, symbol_type: "None | Symbol" = None) -> None:
        self.name: str = name
        self.symbol_type: "None | Symbol" = symbol_type
        self.scope: int = 0

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}'" + (
            f", type='{self.symbol_type.name}')" if self.symbol_type else ")"
        )

    __repr__ = __str__


class BuiltinTypeSymbol(Symbol):
    __slots__ = "name"

    def __init__(self, name: str) -> None:
        super().__init__(name)


class VarSymbol(Symbol):
    __slots__ = "name", "symbol_type"

    def __init__(self, name: str, symbol_type: Symbol | None) -> None:
        super().__init__(name, symbol_type)


class FunctionSymbol(Symbol):
    __slots__ = "name", "params", "block_ast", "return_type"

    def __init__(
        self,
        name: str,
        return_type: BuiltinTypeSymbol,
        params: Sequence[Symbol] | None = None,
        block_ast: AST | None = None,
    ) -> None:
        super().__init__(name)
        self.params: list[Symbol] = list(params) if params is not None else []
        self.block_ast = block_ast
        self.return_type = return_type

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params}, return_type={self.return_type})>"

    __repr__ = __str__


class ProcedureSymbol(Symbol):
    __slots__ = "name", "params", "block_ast"

    def __init__(
        self,
        name: str,
        params: Sequence[Symbol] | None = None,
        block_ast: AST | None = None,
    ) -> None:
        super().__init__(name)
        self.params: list[Symbol] = list(params) if params is not None else []
        self.block_ast = block_ast

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params})>"

    __repr__ = __str__


class ProgramSymbol(Symbol):
    def __init__(self) -> None:
        super().__init__("PROGRAM")

    def __str__(self) -> str:
        return "PROGRAM"

    __repr__ = __str__


class Parser:
    __slots__ = "lexer", "current_token"

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = next(lexer)

    def restart(self) -> None:
        self.lexer.restart()
        self.current_token = next(self.lexer)

    def eat(self, token_type: TokenType, *token_types: TokenType) -> None:
        expected = (token_type,) + token_types
        if self.current_token.token_type not in expected:
            line_no, pos = self.lexer.get_cursor_pos()
            raise ParserError(
                f"parsing error at line no {line_no}:"
                f" expected {expected} as pos {pos}, got {self.current_token.token_type}",
                ErrorCode.UNEXPECTED_TOKEN,
                self.current_token,
            )
        self.current_token = next(self.lexer)

    def program(self) -> Program:
        """
        program:
            PROGRAM ID SEMI block DOT
        """
        self.eat(TokenType.PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.eat(TokenType.SEMI)
        block_node = self.block()
        self.eat(TokenType.DOT)
        return Program(prog_name, block_node)

    def block(self) -> Block:
        """
        block:
            declarations compound_statement
        """
        nodes = self.declarations()
        comp_node = self.compound_statement()
        return Block(tuple(nodes), comp_node)

    def declarations(self) -> list[VarDecl | Procedure | Function]:
        """
        declarations:
            (VAR variable_declaration SEMI)* (procedure_declaration | function_declaration)*
        """
        decls: list[VarDecl | Procedure | Function] = []
        while self.current_token.token_type == TokenType.VAR:
            self.eat(TokenType.VAR)
            var_decl = self.variable_declaration()
            decls.extend(var_decl)
            self.eat(TokenType.SEMI)
        while self.current_token.token_type in (
            TokenType.PROCEDURE,
            TokenType.FUNCTION,
        ):
            if self.current_token.token_type == TokenType.PROCEDURE:
                decls.append(self.procedure_declaration())
            elif self.current_token.token_type == TokenType.FUNCTION:
                decls.append(self.function_declaration())
        return decls

    def function_declaration(self) -> Function:
        """
        function_declaration:
            FUNCTION ID OPEN_PARANTH formal_parameter_list CLOSE_PARANTH
            COLON type_spec SEMI block SEMI
        """
        self.eat(TokenType.FUNCTION)
        func_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.OPEN_PARANTH)
        params = self.formal_parameter_list()
        self.eat(TokenType.CLOSE_PARANTH)
        self.eat(TokenType.COLON)
        return_type = self.type_spec()
        self.eat(TokenType.SEMI)
        block = self.block()
        self.eat(TokenType.SEMI)
        return Function(func_name, block, tuple(params), return_type)

    def procedure_declaration(self) -> Procedure:
        """
        procedure_declaration:
            PROCEDURE ID OPEN_PARANTH formal_parameter_list CLOSE_PARANTH SEMI block SEMI
        """
        self.eat(TokenType.PROCEDURE)
        proc_name = self.current_token.value
        self.eat(TokenType.ID)
        params = []
        if self.current_token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            params = self.formal_parameter_list()
            self.eat(TokenType.CLOSE_PARANTH)
        self.eat(TokenType.SEMI)
        block = self.block()
        self.eat(TokenType.SEMI)
        return Procedure(proc_name, block, tuple(params))

    def formal_parameter_list(self) -> list[Param]:
        """
        formal_parameter_list
            formal_parameters (SEMI formal_parameter_list)?
        """
        params = self.formal_parameters()
        if self.current_token.token_type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            params.extend(self.formal_parameter_list())
        return params

    def formal_parameters(self) -> list[Param]:
        """
        formal_parameters:
            ID (COMMA ID)* COLON type_spec
        """
        names = [self.current_token]
        self.eat(TokenType.ID)
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            names.append(self.current_token)
            self.eat(TokenType.ID)
        self.eat(TokenType.COLON)
        param_type = self.type_spec()
        return [Param(Var(name), param_type) for name in names]

    def variable_declaration(self) -> list[VarDecl]:
        """
        variable_declaration:
            ID (COMMA ID)* COLON type_spec
        """
        var_nodes = [Var(self.current_token)]
        self.eat(TokenType.ID)

        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(TokenType.ID)

        self.eat(TokenType.COLON)

        type_node = self.type_spec()
        return [VarDecl(var_node, type_node) for var_node in var_nodes]

    def type_spec(self) -> Type:
        """
        type_spec:
            INTEGER | REAL | BOOLEAN
        """
        token = self.current_token
        self.eat(TokenType.INTEGER, TokenType.REAL, TokenType.BOOLEAN)
        return Type(token)

    def compound_statement(self) -> Compound:
        """
        compound_statement:
            BEGIN statement_list END
        """
        self.eat(TokenType.BEGIN)
        nodes = self.statement_list()
        self.eat(TokenType.END)
        return Compound(tuple(nodes))

    def statement_list(self) -> list[AST]:
        """
        statement_list:
            statement (SEMI statement)*
        """
        results = [self.statement()]
        while self.current_token.token_type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            results.append(self.statement())
        if self.current_token.token_type == TokenType.ID:
            lineno, col = self.lexer.get_cursor_pos()
            raise ParserError(
                f"unassigned variable {self.current_token.value} at {lineno} line number, {col} column",
                ErrorCode.UNASSIGNED_VARIABLE,
                self.current_token,
            )
        return results

    def statement(self) -> AST:
        """
        statement:
            compound_statement |
            call_statement |
            assignment_statement |
            exit_statement |
            NoOp
        """
        if self.current_token.token_type == TokenType.BEGIN:
            return self.compound_statement()
        if self.current_token.token_type == TokenType.ID and self.lexer.char == "(":
            return self.call_statement()
        if self.current_token.token_type == TokenType.ID:
            return self.assignement_statement()
        if self.current_token.token_type == TokenType.EXIT:
            return self.exit_statement()
        return NoOp()

    def exit_statement(self) -> Exit:
        """
        exit_statement:
            EXIT (OPEN_PARANTH expr CLOSE_PARANTH)?
        """
        self.eat(TokenType.EXIT)
        expr = None
        if self.current_token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            expr = self.expr()
            self.eat(TokenType.CLOSE_PARANTH)
        return Exit(expr=expr)

    def assignement_statement(self) -> AST:
        """
        assignement_statement:
            variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        return Assign(left, token, right)

    def variable(self) -> Var:
        """
        var:
            ID
        """
        node = Var(self.current_token)
        self.eat(TokenType.ID)
        return node

    def factor(self) -> AST:
        """
        factor:
            (PLUS | MINUS) factor |
            (INTEGER_CONST | REAL_CONST) |
            OPEN_PARANTH expr CLOSE_PARANTH |
            call_statement |
            variable
        """
        token = self.current_token
        if token.token_type in (TokenType.MINUS, TokenType.PLUS):
            self.eat(TokenType.PLUS, TokenType.MINUS)
            return UnaryOp(token, self.factor())
        if token.token_type in (TokenType.INTEGER_CONST, TokenType.REAL_CONST):
            self.eat(TokenType.INTEGER_CONST, TokenType.REAL_CONST)
            return Num(token)
        if token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            result = self.expr()
            self.eat(TokenType.CLOSE_PARANTH)
            return result
        if token.token_type == TokenType.ID and self.lexer.char == "(":
            return self.call_statement()
        return self.variable()

    def term(self) -> AST:
        """
        term:
            factor ((MULT | DIV | FLOAT_DIV) factor)*
        """
        node = self.factor()

        while self.current_token.token_type in (
            TokenType.MULTIPLICATION,
            TokenType.INTEGER_DIV,
            TokenType.FLOAT_DIV,
        ):
            token = self.current_token
            self.eat(
                TokenType.MULTIPLICATION, TokenType.INTEGER_DIV, TokenType.FLOAT_DIV
            )
            node = BinOp(node, token, self.factor())

        return node

    def call_statement(self) -> AST:
        """
        call_statement:
            ID OPEN_PARANTH expr (COMMA expr)* CLOSE_PARANTH
        """
        proc_token = self.current_token
        proc_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.OPEN_PARANTH)
        params = []
        if self.current_token.token_type != TokenType.CLOSE_PARANTH:
            params.append(self.expr())
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            params.append(self.expr())
        self.eat(TokenType.CLOSE_PARANTH)
        return ProcedureCall(proc_name, tuple(params), proc_token)

    def expr(self) -> AST:
        """
        expr:
            term ((MINUS | PLUS) term)*
        """
        node = self.term()

        while self.current_token.token_type in (TokenType.MINUS, TokenType.PLUS):
            token = self.current_token
            self.eat(TokenType.PLUS, TokenType.MINUS)
            node = BinOp(node, token, self.term())
        return node

    def parse(self) -> AST:
        node = self.program()
        if self.current_token.token_type != TokenType.EOF:
            raise ParserError(
                "EOF not found", ErrorCode.EOF_NOT_FOUND, self.current_token
            )
        self.restart()
        return node
