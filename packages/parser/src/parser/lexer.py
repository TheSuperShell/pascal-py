from parser.errors import LexerError
from parser.token import Token, TokenType


_RESERVED_KEYWORDS: dict[str, Token] = {
    "BEGIN": Token.begin(),
    "END": Token.end(),
    "DIV": Token.int_div(),
    "PROGRAM": Token.program(),
    "VAR": Token.var(),
    "INTEGER": Token.integer(),
    "REAL": Token.real(),
    "BOOLEAN": Token.boolean(),
    "PROCEDURE": Token.procedure(),
    "FUNCTION": Token.function(),
    "EXIT": Token.exit(),
    "TRUE": Token.const_bool(True),
    "FALSE": Token.const_bool(False),
    "AND": Token.And(),
    "OR": Token.Or(),
    "NOT": Token.Not(),
    "IF": Token.If(),
    "ELSE": Token.Else(),
    "THEN": Token.then(),
    "CHAR": Token.char(),
    "STRING": Token.string(),
    "WHILE": Token.While(),
    "DO": Token.do(),
    "FOR": Token.For(),
    "TO": Token.to(),
    "CONTINUE": Token.Continue(),
    "BREAK": Token.Break(),
    "TYPE": Token.Type(),
    "CONST": Token.const(),
}


class Lexer:
    __slots__ = ("file_text", "index", "stop", "char")

    def __init__(self, file_text: str) -> None:
        self.file_text: str = file_text.strip()
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
            return Token.const_char(self.file_text[current_index])
        return Token.const_string(
            self.file_text[current_index:end_index].replace("\\", "")
        )

    def number(self) -> Token:
        current_index = self.index
        while self.char is not None and self.char.isdigit():
            self.advance()
        if self.char != ".":
            return Token.const_int(self.file_text[current_index : self.index])
        self.advance()
        while self.char is not None and self.char.isdigit():
            self.advance()
        return Token.const_float(self.file_text[current_index : self.index])

    def _id(self) -> Token:
        current_index = self.index
        while self.char is not None and (self.char.isalnum() or self.char == "_"):
            self.advance()
        word = self.file_text[current_index : self.index]
        return _RESERVED_KEYWORDS.get(word.upper(), Token.Id(word))

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
            return Token(TokenType.EOF)
        if self.char == "+":
            self.advance()
            return Token.plus()
        if self.char == "-":
            self.advance()
            return Token.minus()
        if self.char == "*":
            self.advance()
            return Token.mult()
        if self.char == "/":
            self.advance()
            return Token.float_div()
        if self.char == "=":
            self.advance()
            return Token.eq()
        if self.char == ">":
            self.advance()
            if self.char == "=":
                self.advance()
                return Token.get()
            return Token.gt()
        if self.char == "<":
            self.advance()
            if self.char == ">":
                self.advance()
                return Token.neq()
            if self.char == "=":
                self.advance()
                return Token.let()
            return Token.lt()
        if self.char == "(":
            self.advance()
            return Token.open_p()
        if self.char == ")":
            self.advance()
            return Token.close_p()
        if self.char.isdigit():
            return self.number()
        if self.char == "'":
            return self.string()
        if self.char.isalnum() or self.char == "_":
            return self._id()
        if self.char == ";":
            self.advance()
            return Token.semi()
        if self.char == ",":
            self.advance()
            return Token.comma()
        if self.char == ":":
            if self.peek() == "=":
                self.advance()
                self.advance()
                return Token.assign()
            self.advance()
            return Token.colon()
        if self.char == ".":
            self.advance()
            return Token.dot()
        lineno, pos = self.get_cursor_pos()
        raise LexerError(f"uknown symbol {self.char} on {lineno} line number at {pos}")
