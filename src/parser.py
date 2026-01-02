from abc import ABC, abstractmethod

from src.lexer import Lexer

from src.token import Token, TokenType


class ParsingError(Exception): ...


class AST(ABC):
    __slots__ = "token"

    def __init__(self, token: Token) -> None:
        self.token = token

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __str__(self) -> str: ...


class BinOp(AST):
    __slots__ = "op", "left", "right"

    def __init__(self, left: AST, op: Token, right: AST) -> None:
        super().__init__(op)
        self.op = op
        self.left = left
        self.right = right

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinOp):
            return False
        return (
            self.left == other.left
            and self.op == other.op
            and self.right == other.right
        )

    def __repr__(self) -> str:
        return f"BinOp(\n\tleft={self.left},\n\top={self.op},\n\tright={self.right})"

    def __str__(self) -> str:
        return f"{self.left}{self.op.value}{self.right}"


class Num(AST):
    __slots__ = "value"

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = int(token.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Num):
            return False
        return self.value == other.value

    def __repr__(self) -> str:
        return f"Num({self.value})"

    def __str__(self) -> str:
        return f"{self.value}"


class UnaryOp(AST):
    __slots__ = "op", "expr"

    def __init__(self, op: Token, expr: AST) -> None:
        super().__init__(op)
        self.op = op
        self.expr = expr

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnaryOp):
            return False
        return self.expr == other.expr and self.op == other.op

    def __repr__(self) -> str:
        return f"UnaryOp(\n\top={self.op},\n\texpr={self.expr}\n)"

    def __str__(self) -> str:
        return f"{self.op.value}{str(self.expr)}"


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

    def factor(self) -> AST:
        token = self.current_token
        if token.token_type in (TokenType.MINUS, TokenType.PLUS):
            self.eat(TokenType.PLUS, TokenType.MINUS)
            return UnaryOp(token, self.factor())
        if token.token_type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        if token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            result = self.expr()
            self.eat(TokenType.CLOSE_PARANTH)
            return result
        raise ParsingError(
            f"expected {TokenType.INTEGER} or {TokenType.OPEN_PARANTH}, got {token.token_type}"
        )

    def term(self) -> AST:
        node = self.factor()

        while self.current_token.token_type in (
            TokenType.MULTIPLICATION,
            TokenType.DIVISION,
        ):
            token = self.current_token
            self.eat(TokenType.MULTIPLICATION, TokenType.DIVISION)
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
        return self.expr()
