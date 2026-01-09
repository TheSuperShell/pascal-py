from abc import ABC
from collections.abc import Callable, Sequence
from typing import Any

from parser.parser import AST


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


class CallableSymbol(Symbol):
    __slots__ = "name", "params", "block_ast", "return_type"

    def __init__(
        self,
        name: str,
        return_type: BuiltinTypeSymbol | None = None,
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


class BuiltinCallableSymbol(Symbol):
    __slots__ = "name", "params", "return_type", "func"

    def __init__(
        self,
        name: str,
        func: Callable[..., Any],
        params: Sequence[Symbol] | None = None,
        return_type: Symbol | None = None,
    ) -> None:
        super().__init__(name)
        self.params = list(params) if params else None
        self.return_type = return_type
        self.func = func

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params}, return_type={self.return_type})>"

    __repr__ = __str__


class ProgramSymbol(Symbol):
    def __init__(self) -> None:
        super().__init__("PROGRAM")

    def __str__(self) -> str:
        return "PROGRAM"

    __repr__ = __str__
