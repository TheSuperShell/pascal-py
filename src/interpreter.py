from src.lexer import Lexer
from src.token import TokenType


class InterpreterError(Exception): ...


class Interpreter:
    __slots__ = "lexer", "current_token"

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = next(lexer)

    def eat(self, token_type: TokenType) -> None:
        if self.current_token.token_type != token_type:
            raise InterpreterError(
                f"Unexpected type, expected {token_type}, got {self.current_token.token_type}"
            )
        self.current_token = next(self.lexer)

    def factor(self) -> int:
        token = self.current_token
        if token.token_type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return int(token.value)
        elif token.token_type == TokenType.OPEN_PARANTH:
            self.eat(TokenType.OPEN_PARANTH)
            result = self.expr()
            self.eat(TokenType.CLOSE_PARANTH)
            return result
        raise InterpreterError(
            f"expected {TokenType.INTEGER} or {TokenType.OPEN_PARANTH}, got {token.token_type}"
        )

    def term(self) -> int:
        result = self.factor()

        while self.current_token.token_type in (
            TokenType.MULTIPLICATION,
            TokenType.DIVISION,
        ):
            token = self.current_token
            if token.token_type == TokenType.MULTIPLICATION:
                self.eat(TokenType.MULTIPLICATION)
                result = result * self.factor()
            elif token.token_type == TokenType.DIVISION:
                self.eat(TokenType.DIVISION)
                result = result // self.factor()

        return result

    def expr(self) -> int:
        result = self.term()

        while self.current_token.token_type in (TokenType.MINUS, TokenType.PLUS):
            token = self.current_token
            if token.token_type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                result = result + self.term()
            elif token.token_type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                result = result - self.term()
        return result
