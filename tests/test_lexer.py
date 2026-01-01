from src.lexer import Lexer
from src.token import Token, TokenType


def test_lexer_math():
    lexer = Lexer("10 + 9 - 2 / 4 * 123")
    assert list(lexer) == [
        Token(TokenType.INTEGER, "10"),
        Token(TokenType.PLUS),
        Token(TokenType.INTEGER, "9"),
        Token(TokenType.MINUS),
        Token(TokenType.INTEGER, "2"),
        Token(TokenType.DIVISION),
        Token(TokenType.INTEGER, "4"),
        Token(TokenType.MULTIPLICATION),
        Token(TokenType.INTEGER, "123"),
        Token(TokenType.EOF),
    ]


def test_remove_spaces():
    lexer_space = Lexer("10   +\t20/\n30")
    lexer = Lexer("10+20/30")
    assert list(lexer) == list(lexer_space)
