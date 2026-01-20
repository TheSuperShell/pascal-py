from parser.errors import LexerError
from parser.token import Token, TokenType


class Lexer:
    __slots__ = ("file_text", "index", "stop", "char", "reserved_keywords")

    def __init__(self, file_text: str) -> None:
        self.file_text: str = file_text.strip()
        self.reserved_keywords = TokenType.get_reserved_keywords()
        self.restart()

    def __iter__(self) -> "Lexer":
        return self

    def get_cursor_pos(self) -> tuple[int, int]:
        lines = self.file_text[: self.index].split("\n")
        return len(lines), len(lines[-1])

    def restart(self) -> None:
        self.index: int = 0
        self.char: str | None = self.file_text[0]
        self.stop: bool = False

    def advance(self) -> None:
        self.index += 1
        if self.index > len(self.file_text) - 1:
            self.char = None
            return
        self.char = self.file_text[self.index]

    def skip_space(self) -> None:
        if self.index >= len(self.file_text) - 1:
            return
        while self.file_text[self.index] in (" ", "\t", "\n"):
            self.advance()

    def comment(self) -> None:
        while self.file_text[self.index] != "}":
            self.advance()
        self.advance()

    def string(self) -> Token:
        self.advance()
        current_index = self.index
        while not (self.peek() == "'" and self.char != "\\"):
            self.advance()
        self.advance()
        end_index = self.index
        self.advance()
        if end_index - current_index == 1:
            return Token.with_value(TokenType.CHAR_CONST, self.file_text[current_index])
        return Token.with_value(
            TokenType.STRING_CONST,
            self.file_text[current_index:end_index].replace("\\", ""),
        )

    def number(self) -> Token:
        current_index = self.index
        while self.char is not None and self.char.isdigit():
            self.advance()
        next_char = self.peek()
        if self.char != "." or next_char is None or not next_char.isdigit():
            return Token.with_value(
                TokenType.INTEGER_CONST, self.file_text[current_index : self.index]
            )
        self.advance()
        while self.char is not None and self.char.isdigit():
            self.advance()
        return Token.with_value(
            TokenType.REAL_CONST, self.file_text[current_index : self.index]
        )

    def _id(self) -> Token:
        current_index = self.index
        while self.char is not None and (self.char.isalnum() or self.char == "_"):
            self.advance()
        word = self.file_text[current_index : self.index]
        token_type = self.reserved_keywords.get(word.upper(), TokenType.ID)
        return Token.with_value(token_type, word)

    def peek(self) -> str | None:
        peek_pos = self.index + 1
        if peek_pos > len(self.file_text) - 1:
            return None
        return self.file_text[peek_pos]

    def __next__(self) -> Token:
        if self.stop:
            self.restart()
            raise StopIteration()

        self.skip_space()
        while self.char == "{":
            self.comment()
            self.skip_space()
        if self.char is None:
            self.stop = True
            return Token.new(TokenType.EOF)
        if self.char in self.reserved_keywords:
            char = self.char
            self.advance()
            return Token.new(self.reserved_keywords[char])
        if self.char == ">":
            self.advance()
            if self.char == "=":
                self.advance()
                return Token.new(TokenType.MORE_OR_EQUAL)
            return Token.new(TokenType.MORE)
        if self.char == "<":
            self.advance()
            if self.char == ">":
                self.advance()
                return Token.new(TokenType.NOT_EQUAL)
            if self.char == "=":
                self.advance()
                return Token.new(TokenType.LESS_OR_EQUAL)
            return Token.new(TokenType.LESS)
        if self.char.isdigit():
            return self.number()
        if self.char == "'":
            return self.string()
        if self.char == ":":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token.new(TokenType.ASSIGN)
            self.advance()
            return Token.new(TokenType.COLON)
        if self.char.isalnum() or self.char == "_":
            return self._id()
        lineno, pos = self.get_cursor_pos()
        raise LexerError(f"uknown symbol {self.char} on {lineno} line number at {pos}")
