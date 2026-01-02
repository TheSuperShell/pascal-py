from src.token import Token, TokenType


class ScriptParsingError(Exception): ...


_RESERVED_KEYWORDS: dict[str, Token] = {
    "BEGIN": Token.begin(),
    "END": Token.end(),
    "DIV": Token.div(),
}


class Lexer:
    __slots__ = ("file_text", "index", "stop", "char")

    def __init__(self, file_text: str) -> None:
        self.file_text: str = file_text.strip()
        self.index: int = 0
        self.char: str | None = file_text[0]
        self.stop: bool = False

    def __iter__(self) -> "Lexer":
        return self

    def advance(self) -> None:
        self.index += 1
        if self.index > len(self.file_text) - 1:
            self.char = None
            return
        self.char = self.file_text[self.index]

    def skip_space(self) -> None:
        while self.file_text[self.index] in (" ", "\t", "\n"):
            self.advance()

    def integer(self) -> Token:
        current_index = self.index
        while self.char is not None and self.char.isdigit():
            self.advance()
        return Token.integer(self.file_text[current_index : self.index])

    def _id(self) -> Token:
        current_index = self.index
        while self.char is not None and (self.char.isalnum() or self.char == "_"):
            self.advance()
        word = self.file_text[current_index : self.index].upper()
        return _RESERVED_KEYWORDS.get(word, Token.Id(word))

    def peek(self) -> str | None:
        peek_pos = self.index + 1
        if peek_pos > len(self.file_text) - 1:
            return None
        return self.file_text[peek_pos]

    def __next__(self) -> Token:
        if self.stop:
            self.index = 0
            self.stop = False
            raise StopIteration()

        if self.char is None:
            self.stop = True
            return Token(TokenType.EOF)

        self.skip_space()
        if self.char == "+":
            self.advance()
            return Token.plus()
        if self.char == "-":
            self.advance()
            return Token.minus()
        if self.char == "*":
            self.advance()
            return Token.mult()
        if self.char == "(":
            self.advance()
            return Token.open_p()
        if self.char == ")":
            self.advance()
            return Token.close_p()
        if self.char.isdigit():
            return self.integer()
        if self.char.isalnum() or self.char == "_":
            return self._id()
        if self.char == ";":
            self.advance()
            return Token.semi()
        if self.char == ":":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token.assign()
        if self.char == ".":
            self.advance()
            return Token.dot()
        raise ScriptParsingError(f"Uknown symbol {self.char}")
