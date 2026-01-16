from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from parser.errors import ErrorCode, ParserError
from parser.lexer import Lexer

from parser.token import Token, TokenType


class AST[S](ABC):
    __slots__ = "type_symbol", "symbol"

    def __init__(self) -> None:
        self.symbol: S | None = None
        self.type_symbol: S | None = None

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __str__(self) -> str: ...


@dataclass(slots=True)
class BinOp[S](AST[S]):
    left: AST[S]
    token: Token
    right: AST[S]
    type_symbol: S | None = None

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


@dataclass(slots=True)
class Literal[T, S](AST[S]):
    token: Token
    cast: Callable[[str], T]
    type_symbol: S | None = None

    @property
    def value(self) -> T:
        return self.cast(self.token.value)

    def __str__(self) -> str:
        return f"Literal({self.value})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Literal):
            return False
        return self.token == other.token


@dataclass(slots=True)
class UnaryOp[S](AST[S]):
    token: Token
    expr: AST[S]
    type_symbol: S | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnaryOp):
            return False
        return self.expr == other.expr and self.token == other.token

    def __repr__(self) -> str:
        return f"UnaryOp(\n\top={self.token},\n\texpr={self.expr}\n)"

    def __str__(self) -> str:
        return f"{self.token.value}{str(self.expr)}"


@dataclass(slots=True, frozen=True)
class Compound[S](AST[S]):
    children: tuple[AST[S], ...]

    def __str__(self) -> str:
        children = "\n".join([str(c) for c in self.children])
        return f"BEGIN\n{children}\nEND"

    def __repr__(self) -> str:
        return f"Compund({self.children})"


@dataclass(slots=True, frozen=True)
class Assign[S](AST[S]):
    left: "Var[S]"
    token: Token
    right: AST[S]

    def __str__(self) -> str:
        return f"{self.left}:={self.right}"

    def __repr__(self) -> str:
        return f"Assign(left={self.left}, right={self.right})"


@dataclass(slots=True)
class Var[S](AST[S]):
    token: Token
    type_symbol: S | None = None
    symbol: S | None = None

    @property
    def value(self) -> str:
        return self.token.value

    def __repr__(self) -> str:
        return f"Var({self.value})"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NoOp[S](AST[S]):
    def __str__(self) -> str:
        return "\\N"

    def __repr__(self) -> str:
        return "NoOp()"


@dataclass(frozen=True, slots=True)
class Program[S](AST[S]):
    name: str
    block: "Block[S]"

    def __str__(self) -> str:
        return f"-- {self.name} --\n"

    def __repr__(self) -> str:
        return f"Program(name={self.name}, block={self.block})"


type Declaration[S] = (
    ConstDecl[S] | TypeDecl[S] | VarDecl[S] | Procedure[S] | Function[S]
)


@dataclass(frozen=True, slots=True)
class Block[S](AST[S]):
    declarations: tuple[Declaration[S], ...]
    compund_statement: Compound[S]

    def __str__(self) -> str:
        return str(self.compund_statement)

    def __repr__(self) -> str:
        return f"Block({self.declarations=}, {self.compund_statement=})"


@dataclass(frozen=True, slots=True)
class VarDecl[S](AST[S]):
    var_node: Var[S]
    type_node: "Type[S]"
    default_value: Literal[Any, S] | None = None

    def __str__(self) -> str:
        return f"{self.var_node}: {self.type_node}"

    def __repr__(self) -> str:
        return f"VarDecl({self.var_node}:{self.type_node})"


@dataclass(frozen=True, slots=True)
class TypeDecl[S](AST[S]):
    var_node: Var[S]
    type_node: "Type[S]"

    def __str__(self) -> str:
        return f"{self.var_node}: {self.type_node}"

    def __repr__(self) -> str:
        return f"TypeDecl({self.var_node}:{self.type_node})"


@dataclass(frozen=True, slots=True)
class ConstDecl[S](AST[S]):
    var_node: "Var[S]"
    literal: Literal[Any, S]

    def __str__(self) -> str:
        return f"{self.var_node} = {self.literal}"

    def __repr__(self) -> str:
        return f"ConstDecl({self.var_node}:{self.literal})"


type Type[S] = StandardType[S] | Range[S] | Enum[S] | Array[S] | DynamicArray[S]


@dataclass(frozen=True, slots=True)
class Array[S](AST[S]):
    index_type: "Range[S] | StandardType[S]"
    element_type: Type[S]
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.element_type}[{self.index_type}]"

    def __repr__(self) -> str:
        return f"ARRAY({self.index_type=}, {self.element_type=})"


@dataclass(frozen=True, slots=True)
class DynamicArray[S](AST[S]):
    element_type: Type[S]
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.element_type}[]"

    def __repr__(self) -> str:
        return f"DynamicArray({self.element_type=})"


@dataclass(slots=True)
class StandardType[S](AST[S]):
    token: Token
    type_symbol: S | None = None

    @property
    def value(self) -> str:
        return self.token.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Procedure[S](AST[S]):
    name: str
    block: Block[S]
    params: "tuple[Param[S], ...]"

    def __str__(self) -> str:
        params = ", ".join(str(param) for param in self.params)
        return f"{self.name}({params}):\n{self.block}"

    def __repr__(self) -> str:
        return f"Procedure({self.name=}, {self.params=}, {self.block=})"


@dataclass(frozen=True, slots=True)
class Function[S](AST[S]):
    name: str
    block: Block[S]
    params: "tuple[Param[S], ...]"
    return_type: Type[S]

    def __str__(self) -> str:
        params = ", ".join(str(param) for param in self.params)
        return f"{self.name}({params}): {self.return_type}"

    def __repr__(self) -> str:
        return f"Function({self.name=}, {self.params=}, {self.return_type=}, {self.block=})"


@dataclass(slots=True)
class Param[S](AST[S]):
    var_node: Var[S]
    type_node: Type[S]
    out: bool
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.var_node}: {self.type_node}"

    def __repr__(self) -> str:
        return f"Param({self.var_node=}, {self.type_node})"


@dataclass(slots=True)
class Call[S](AST[S]):
    name: str
    actual_params: tuple[AST[S], ...]
    token: Token
    proc_symbol: S | None = None
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.name}({self.actual_params})"

    def __repr__(self) -> str:
        return f"ProcedureCall({self.name=}, {self.actual_params=})"


@dataclass(slots=True, frozen=True)
class Exit[S](AST[S]):
    expr: None | AST[S] = None

    def __str__(self) -> str:
        return "Exit" + (f": {self.expr}" if self.expr else "")

    def __repr__(self) -> str:
        return f"Exit({self.expr=})"


@dataclass(slots=True, frozen=True)
class Condition[S](AST[S]):
    condition: AST[S]
    expr: AST[S]

    def __str__(self) -> str:
        return f"({self.condition}) -> {self.expr}"

    def __repr__(self) -> str:
        return f"Condition({self.condition}, {self.expr=})"


@dataclass(slots=True, frozen=True)
class WhileStatement[S](AST[S]):
    condition: AST[S]
    expr: AST[S]

    def __str__(self) -> str:
        return f"WHILE ({self.condition}) DO {self.expr}"

    def __repr__(self) -> str:
        return f"WhileStatement({self.condition}, {self.expr=})"


@dataclass(slots=True, frozen=True)
class IfStatement[S](AST[S]):
    main_condition: Condition[S]
    secondary_conditions: tuple[Condition[S], ...] = ()
    else_condition: AST[S] | None = None

    def __str__(self) -> str:
        secondary = "\n".join(f"else if {expr}" for expr in self.secondary_conditions)
        return f"if {self.main_condition}\n{secondary}" + (
            f"else {self.else_condition}" if self.else_condition else ""
        )

    def __repr__(self) -> str:
        return f"IfStatement({self.main_condition=}, {self.secondary_conditions=}, {self.else_condition=})"


@dataclass(slots=True, frozen=True)
class ForStatement[S](AST[S]):
    var: Var[S]
    init_state: AST[S]
    end_state: AST[S]
    expr: AST[S]

    def __str__(self) -> str:
        return (
            f"for {self.var} from {self.init_state} to {self.end_state} do {self.expr}"
        )

    def __repr__(self) -> str:
        return f"ForStatement({self.var=}, {self.init_state=}, {self.end_state=}, {self.expr=})"


@dataclass(slots=True, frozen=True)
class ForInStatement[S](AST[S]):
    var: Var[S]
    range_expr: "Range[S] | StandardType[S]"
    expr: AST[S]

    def __str__(self) -> str:
        return f"for {self.var} in {self.range_expr} do {self.expr}"

    def __repr__(self) -> str:
        return f"ForInStatement({self.var=}, {self.range_expr=}, {self.expr=})"


@dataclass(frozen=True, slots=True)
class Continue[S](AST[S]):
    def __str__(self) -> str:
        return "CONTINUE"

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True, slots=True)
class Break[S](AST[S]):
    def __str__(self) -> str:
        return "BREAK"

    def __repr__(self) -> str:
        return str(self)


@dataclass(slots=True)
class Range[S](AST[S]):
    start_val: Literal[Any, S] | Var[S]
    end_val: Literal[Any, S] | Var[S]
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.start_val}..{self.end_val}"

    def __repr__(self) -> str:
        return f"Range({self.start_val}, {self.end_val})"


@dataclass(slots=True)
class Enum[S](AST[S]):
    items: list[Var[S]]
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"({self.items})"

    def __repr__(self) -> str:
        return f"Enum({self.items})"


@dataclass(slots=True)
class IndexOf[S](AST[S]):
    var_node: Var[S]
    index_value: AST[S]
    other_indicies: list[AST[S]]
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.var_node}[{self.index_value}]"

    def __repr__(self) -> str:
        return f"IndexOf({self.var_node=}, {self.index_value=})"


@dataclass(slots=True)
class AssignIndex[S](AST[S]):
    left: IndexOf[S]
    right: AST[S]
    type_symbol: S | None = None

    def __str__(self) -> str:
        return f"{self.left} := {self.right}"

    def __repr__(self) -> str:
        return f"AssignIndex({self.left=}, {self.right=})"


class Parser[S]:
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

    def program(self) -> Program[S]:
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
        return Program[S](prog_name, block_node)

    def block(self) -> Block[S]:
        """
        block:
            declarations compound_statement
        """
        nodes = self.declarations()
        comp_node = self.compound_statement()
        return Block[S](tuple(nodes), comp_node)

    def declarations(
        self,
    ) -> list[Declaration[S]]:
        """
        declarations:
            (
                CONST (const_declaration SEMI)+ |
                TYPE (type_declaration SEMI)+ |
                VAR (variable_declaration SEMI)+ |
                procedure_declaration |
                function_declaration
            )*
        """
        decls: list[Declaration[S]] = []
        while self.current_token.token_type in (
            TokenType.VAR,
            TokenType.PROCEDURE,
            TokenType.FUNCTION,
            TokenType.TYPE,
            TokenType.CONST,
        ):
            if self.current_token.token_type == TokenType.CONST:
                self.eat(TokenType.CONST)
                decls.extend(self.const_declaration())
                self.eat(TokenType.SEMI)
                while self.current_token.token_type == TokenType.ID:
                    decls.extend(self.const_declaration())
                    self.eat(TokenType.SEMI)
            if self.current_token.token_type == TokenType.TYPE:
                self.eat(TokenType.TYPE)
                decls.extend(self.type_declaration())
                self.eat(TokenType.SEMI)
                while self.current_token.token_type == TokenType.ID:
                    decls.extend(self.type_declaration())
                    self.eat(TokenType.SEMI)
            if self.current_token.token_type == TokenType.VAR:
                self.eat(TokenType.VAR)
                decls.extend(self.variable_declaration())
                self.eat(TokenType.SEMI)
                while self.current_token.token_type == TokenType.ID:
                    decls.extend(self.variable_declaration())
                    self.eat(TokenType.SEMI)
            elif self.current_token.token_type == TokenType.PROCEDURE:
                decls.append(self.procedure_declaration())
            elif self.current_token.token_type == TokenType.FUNCTION:
                decls.append(self.function_declaration())
        return decls

    def const_declaration(self) -> list[ConstDecl[S]]:
        """
        const_declaration:
            ID (COMMA ID)* EQUAL literal
        """
        names = [self.current_token]
        self.eat(TokenType.ID)
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            names.append(self.current_token)
            self.eat(TokenType.ID)
        self.eat(TokenType.EQUAL)
        literal_val = self.literal()
        return [ConstDecl[S](Var(name), literal_val) for name in names]

    def type_declaration(self) -> list[TypeDecl[S]]:
        """
        type_declaration:
            ID (COMMA ID)* EQUAL type_spec
        """
        type_names = [self.current_token]
        self.eat(TokenType.ID)
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            type_names.append(self.current_token)
            self.eat(TokenType.ID)
        self.eat(TokenType.EQUAL)
        type_spec = self.type_spec()
        return [TypeDecl[S](Var[S](name), type_spec) for name in type_names]

    def function_declaration(self) -> Function[S]:
        """
        function_declaration:
            FUNCTION ID (OPEN_PARANTH formal_parameter_list CLOSE_PARANTH)?
            COLON type_spec SEMI block SEMI
        """
        self.eat(TokenType.FUNCTION)
        func_name = self.current_token.value
        self.eat(TokenType.ID)
        params = []
        if self.current_token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            params = self.formal_parameter_list()
            self.eat(TokenType.CLOSE_PARANTH)
        self.eat(TokenType.COLON)
        return_type = self.type_spec()
        self.eat(TokenType.SEMI)
        block = self.block()
        self.eat(TokenType.SEMI)
        return Function[S](func_name, block, tuple(params), return_type)

    def procedure_declaration(self) -> Procedure[S]:
        """
        procedure_declaration:
            PROCEDURE ID (OPEN_PARANTH formal_parameter_list CLOSE_PARANTH)? SEMI block SEMI
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
        return Procedure[S](proc_name, block, tuple(params))

    def formal_parameter_list(self) -> list[Param[S]]:
        """
        formal_parameter_list
            formal_parameters (SEMI formal_parameter_list)?
        """
        params = self.formal_parameters()
        if self.current_token.token_type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            params.extend(self.formal_parameter_list())
        return params

    def formal_parameters(self) -> list[Param[S]]:
        """
        formal_parameters:
            OUT? ID (COMMA OUT? ID)* COLON type_spec
        """
        out = self.current_token.token_type == TokenType.OUT
        if out:
            self.eat(TokenType.OUT)
        names = [(out, self.current_token)]
        self.eat(TokenType.ID)
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            out = self.current_token.token_type == TokenType.OUT
            if out:
                self.eat(TokenType.OUT)
            names.append((out, self.current_token))
            self.eat(TokenType.ID)
        self.eat(TokenType.COLON)
        param_type = self.type_spec()
        return [Param[S](Var[S](name), param_type, out) for out, name in names]

    def variable_declaration(self) -> list[VarDecl[S]]:
        """
        variable_declaration:
            ID (COMMA ID)* COLON type_spec (EQAUL literal)?
        """
        var_nodes = [Var[S](self.current_token)]
        self.eat(TokenType.ID)

        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(TokenType.ID)

        self.eat(TokenType.COLON)

        type_node = self.type_spec()
        default_value = None
        if self.current_token.token_type == TokenType.EQUAL:
            self.eat(TokenType.EQUAL)
            default_value = self.literal()
        return [
            VarDecl[S](var_node, type_node, default_value) for var_node in var_nodes
        ]

    def range_statement(self) -> Range[S] | StandardType[S]:
        """
        range_statement:
            ID (DOT DOT ID)? | literal DOT DOT literal
        """
        if self.current_token.token_type == TokenType.ID:
            var = self.current_token
            self.eat(TokenType.ID)
            if self.current_token.token_type == TokenType.DOT:
                self.eat(TokenType.DOT)
                self.eat(TokenType.DOT)
                end = self.current_token
                self.eat(TokenType.ID)
                return Range(Var(var), Var(end))
            return StandardType(var)
        start = self.literal()
        self.eat(TokenType.DOT)
        self.eat(TokenType.DOT)
        end = self.literal()
        return Range[S](start, end)

    def type_spec(self) -> Type[S]:
        """
        type_spec:
            INTEGER | REAL | BOOLEAN | STRING | CHAR |
            enum_decl |
            array_decl |
            range_statement
        """
        token = self.current_token
        if self.current_token.token_type in (
            TokenType.ID,
            TokenType.INTEGER,
            TokenType.REAL,
            TokenType.BOOLEAN,
            TokenType.CHAR,
            TokenType.STRING,
        ):
            self.eat(
                TokenType.ID,
                TokenType.INTEGER,
                TokenType.REAL,
                TokenType.BOOLEAN,
                TokenType.STRING,
                TokenType.CHAR,
            )
            return StandardType[S](token)
        if self.current_token.token_type == TokenType.OPEN_PARANTH:
            return self.enum_decl()
        if self.current_token.token_type == TokenType.ARRAY:
            return self.array_decl()
        return self.range_statement()

    def array_decl(self) -> Array[S] | DynamicArray[S]:
        """
        array_decl:
            ARRAY (OPEN_BRACKET range_statement CLOSE_BRACKET)? OF type_spec
        """
        self.eat(TokenType.ARRAY)
        if self.current_token.token_type == TokenType.OPEN_BRACKET:
            self.eat(TokenType.OPEN_BRACKET)
            index_type = self.range_statement()
            self.eat(TokenType.CLOSE_BRACKET)
            self.eat(TokenType.OF)
            element_type = self.type_spec()
            return Array[S](index_type, element_type)
        self.eat(TokenType.OF)
        element_type = self.type_spec()
        return DynamicArray[S](element_type)

    def enum_decl(self) -> Enum[S]:
        """
        enum_decl:
            OPEN_PARANTH variable (COMMA variable)* CLOSE_PARANTH
        """
        self.eat(TokenType.OPEN_PARANTH)
        items = [self.variable()]
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            items.append(self.variable())
        self.eat(TokenType.CLOSE_PARANTH)
        return Enum[S](items)

    def compound_statement(self) -> Compound[S]:
        """
        compound_statement:
            BEGIN statement_list END
        """
        self.eat(TokenType.BEGIN)
        nodes = self.statement_list()
        self.eat(TokenType.END)
        return Compound[S](tuple(nodes))

    def statement_list(self) -> list[AST[S]]:
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

    def statement(self) -> AST[S]:
        """
        statement:
            CONTINUE |
            BREAK |
            compound_statement |
            call_statement |
            assignment_statement |
            index_assignment_statement |
            if_statement |
            while_statement |
            for_statement |
            exit_statement |
            NoOp
        """
        if self.current_token.token_type == TokenType.CONTINUE:
            self.eat(TokenType.CONTINUE)
            return Continue()
        if self.current_token.token_type == TokenType.BREAK:
            self.eat(TokenType.BREAK)
            return Break()
        if self.current_token.token_type == TokenType.BEGIN:
            return self.compound_statement()
        if self.current_token.token_type == TokenType.ID and self.lexer.char == "(":
            return self.call_statement()
        if self.current_token.token_type == TokenType.ID:
            if self.lexer.char == "[":
                return self.index_assignment_statement()
            return self.assignement_statement()
        if self.current_token.token_type == TokenType.IF:
            return self.if_statement()
        if self.current_token.token_type == TokenType.WHILE:
            return self.while_statement()
        if self.current_token.token_type == TokenType.FOR:
            return self.for_statement()
        if self.current_token.token_type == TokenType.EXIT:
            return self.exit_statement()
        return NoOp[S]()

    def index_assignment_statement(self) -> AssignIndex[S]:
        """
        index_assignement_statement:
            index_of_statement ASSIGN expr
        """
        index_of = self.index_of_statement()
        self.eat(TokenType.ASSIGN)
        left = self.expr()
        return AssignIndex[S](index_of, left)

    def for_statement(self) -> ForStatement[S] | ForInStatement[S]:
        """
        for_statement:
            FOR id (ASSIGN expr TO expr | IN range_statement) DO loop_statement
        """
        self.eat(TokenType.FOR)
        var = self.current_token
        self.eat(TokenType.ID)
        if self.current_token.token_type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            init_state = self.expr()
            self.eat(TokenType.TO)
            end_state = self.expr()
            self.eat(TokenType.DO)
            expr = self.statement()
            return ForStatement(Var(var), init_state, end_state, expr)
        self.eat(TokenType.IN)
        range_expr = self.range_statement()
        self.eat(TokenType.DO)
        expr = self.statement()
        return ForInStatement[S](Var(var), range_expr, expr)

    def while_statement(self) -> WhileStatement[S]:
        """
        while_statement:
            WHILE expr DO loop_statement
        """
        self.eat(TokenType.WHILE)
        condition = self.expr()
        self.eat(TokenType.DO)
        expr = self.statement()
        return WhileStatement[S](condition, expr)

    def condition(self) -> Condition[S]:
        """
        condition:
            expr THEN statement
        """
        cond = self.expr()
        self.eat(TokenType.THEN)
        expr = self.statement()
        return Condition[S](cond, expr)

    def if_statement(self) -> AST[S]:
        """
        if_statement:
            IF condition
            (ELSE IF condition)*
            (ELSE statement)?
        """
        self.eat(TokenType.IF)
        main_condition = self.condition()
        other_conditions: list[Condition[S]] = []
        last_condition = None
        while self.current_token.token_type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            if self.current_token.token_type != TokenType.IF:
                last_condition = self.statement()
                break
            self.eat(TokenType.IF)
            other_conditions.append(self.condition())
        return IfStatement[S](main_condition, tuple(other_conditions), last_condition)

    def exit_statement(self) -> Exit[S]:
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
        return Exit[S](expr=expr)

    def assignement_statement(self) -> AST[S]:
        """
        assignement_statement:
            variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        return Assign[S](left, token, right)

    def variable(self) -> Var[S]:
        """
        var:
            ID
        """
        node = Var[S](self.current_token)
        self.eat(TokenType.ID)
        return node

    def literal(self) -> Literal[Any, S]:
        token = self.current_token
        if token.token_type == TokenType.INTEGER_CONST:
            self.eat(TokenType.INTEGER_CONST)
            return Literal[int, S](token, lambda x: int(x))
        if token.token_type == TokenType.REAL_CONST:
            self.eat(TokenType.REAL_CONST)
            return Literal(token, lambda x: float(x))
        if token.token_type in (TokenType.CHAR_CONST, TokenType.STRING_CONST):
            self.eat(TokenType.CHAR_CONST, TokenType.STRING_CONST)
            return Literal[str, S](token, lambda x: x)
        if token.token_type == TokenType.BOOLEAN_CONST:
            self.eat(TokenType.BOOLEAN_CONST)
            return Literal[bool, S](token, lambda x: x.lower() == "true")
        raise ParserError(f"unkown literal {token.token_type}")

    def factor(self) -> AST[S]:
        """
        factor:
            (PLUS | MINUS) factor |
            NOT compare_expr |
            literal |
            OPEN_PARANTH expr CLOSE_PARANTH |
            call_statement |
            index_of_statement |
            variable
        """
        token = self.current_token
        if token.token_type in (TokenType.MINUS, TokenType.PLUS):
            self.eat(TokenType.PLUS, TokenType.MINUS)
            return UnaryOp[S](token, self.factor())
        if token.token_type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp[S](token, self.compare_expr())
        if token.token_type in (
            TokenType.INTEGER_CONST,
            TokenType.REAL_CONST,
            TokenType.CHAR_CONST,
            TokenType.STRING_CONST,
            TokenType.BOOLEAN_CONST,
        ):
            return self.literal()
        if token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            result = self.expr()
            self.eat(TokenType.CLOSE_PARANTH)
            return result
        if token.token_type == TokenType.ID and self.lexer.char == "(":
            return self.call_statement()
        if token.token_type == TokenType.ID and self.lexer.char == "[":
            return self.index_of_statement()
        return self.variable()

    def index_of_statement(self) -> IndexOf[S]:
        """
        index_of_statement:
            ID OPEN_BRACKET expr (COMMA expr)* CLOSE_BRACKET
        """
        var_node = Var[S](self.current_token)
        self.eat(TokenType.ID)
        self.eat(TokenType.OPEN_BRACKET)
        expr = self.expr()
        other_indicies: list[AST[S]] = []
        while self.current_token.token_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            other_indicies.append(self.expr())
        self.eat(TokenType.CLOSE_BRACKET)
        return IndexOf[S](var_node, expr, other_indicies)

    def mult_expr(self) -> AST[S]:
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
            node = BinOp[S](node, token, self.factor())

        return node

    def call_statement(self) -> AST[S]:
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
        return Call[S](proc_name, tuple(params), proc_token)

    def add_expr(self) -> AST[S]:
        """
        add_expr:
            mult_expr ((MINUS | PLUS) mult_expr)*
        """
        node = self.mult_expr()

        while self.current_token.token_type in (TokenType.MINUS, TokenType.PLUS):
            token = self.current_token
            self.eat(TokenType.PLUS, TokenType.MINUS)
            node = BinOp[S](node, token, self.mult_expr())
        return node

    def compare_expr(self) -> AST[S]:
        """
        compare_expr:
            add_expr ((LESS, MORE, LESS_OR_EQUAL, MORE_OR_EQUAL, EQUAL, NOT_EQUAL) add_expr)*
        """
        node = self.add_expr()

        while self.current_token.token_type in (
            TokenType.LESS,
            TokenType.MORE,
            TokenType.LESS_OR_EQUAL,
            TokenType.MORE_OR_EQUAL,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
        ):
            token = self.current_token
            self.eat(
                TokenType.LESS,
                TokenType.MORE,
                TokenType.LESS_OR_EQUAL,
                TokenType.MORE_OR_EQUAL,
                TokenType.EQUAL,
                TokenType.NOT_EQUAL,
            )
            node = BinOp[S](node, token, self.add_expr())
        return node

    def bool_expr(self) -> AST[S]:
        """
        bool_expr:
            compare_expr (AND compare_expr)*
        """
        node = self.compare_expr()

        while self.current_token.token_type == TokenType.AND:
            self.eat(TokenType.AND)
            node = BinOp[S](node, Token.And(), self.compare_expr())
        return node

    def expr(self) -> AST[S]:
        """
        expr:
            bool_expr (OR bool_expr)*
        """
        node = self.bool_expr()
        while self.current_token.token_type == TokenType.OR:
            self.eat(TokenType.OR)
            node = BinOp[S](node, Token.Or(), self.bool_expr())
        return node

    def parse(self) -> AST[S]:
        node = self.program()
        if self.current_token.token_type != TokenType.EOF:
            raise ParserError(
                "EOF not found", ErrorCode.EOF_NOT_FOUND, self.current_token
            )
        self.restart()
        return node
