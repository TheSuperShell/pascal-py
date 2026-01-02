from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.lexer import Lexer

from src.token import Token, TokenType


class ParsingError(Exception): ...


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
    def value(self) -> int:
        return int(self.token.value)

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
class Compund(AST):
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
    declarations: "tuple[VarDecl, ...]"
    compund_statement: Compund

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


class Parser:
    __slots__ = "lexer", "current_token"

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = next(lexer)

    def eat(self, token_type: TokenType, *token_types: TokenType) -> None:
        expected = (token_type,) + token_types
        if self.current_token.token_type not in expected:
            raise ParsingError(
                f"expected {expected}, got {self.current_token.token_type}"
            )
        self.current_token = next(self.lexer)

    def program(self) -> Program:
        self.eat(TokenType.PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.eat(TokenType.SEMI)
        block_node = self.block()
        self.eat(TokenType.DOT)
        return Program(prog_name, block_node)

    def block(self) -> Block:
        nodes = self.declarations()
        comp_node = self.compound_statement()
        return Block(tuple(nodes), comp_node)

    def declarations(self) -> list[VarDecl]:
        decls: list[VarDecl] = []
        if self.current_token.token_type == TokenType.VAR:
            self.eat(TokenType.VAR)
            while self.current_token.token_type == TokenType.ID:
                var_decl = self.variable_declaration()
                decls.extend(var_decl)
                self.eat(TokenType.SEMI)
        return decls

    def variable_declaration(self) -> list[VarDecl]:
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
        token = self.current_token
        self.eat(TokenType.INTEGER, TokenType.REAL)
        return Type(token)

    def compound_statement(self) -> Compund:
        self.eat(TokenType.BEGIN)
        nodes = self.statement_list()
        self.eat(TokenType.END)
        return Compund(tuple(nodes))

    def statement_list(self) -> list[AST]:
        results = [self.statement()]
        while self.current_token.token_type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            results.append(self.statement())
        if self.current_token.token_type == TokenType.ID:
            raise ParsingError(f"unassigned variable {self.current_token.value}")
        return results

    def statement(self) -> AST:
        if self.current_token.token_type == TokenType.BEGIN:
            return self.compound_statement()
        if self.current_token.token_type == TokenType.ID:
            return self.assignement_statement()
        return NoOp()

    def assignement_statement(self) -> AST:
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        return Assign(left, token, right)

    def variable(self) -> Var:
        node = Var(self.current_token)
        self.eat(TokenType.ID)
        return node

    def factor(self) -> AST:
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
        return self.variable()

    def term(self) -> AST:
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

    def expr(self) -> AST:
        node = self.term()

        while self.current_token.token_type in (TokenType.MINUS, TokenType.PLUS):
            token = self.current_token
            self.eat(TokenType.PLUS, TokenType.MINUS)
            node = BinOp(node, token, self.term())
        return node

    def parse(self) -> AST:
        node = self.program()
        if self.current_token.token_type != TokenType.EOF:
            raise ParsingError("EOF not found")
        return node
