from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Symbol(ABC):
    name: str
    symbol_type: "None | Symbol" = None


@dataclass(frozen=True, slots=True)
class BuiltinTypeSymbol(Symbol):
    def __str__(self) -> str:
        return self.name

    __repr__ = __str__


@dataclass(frozen=True, slots=True)
class VarSymbol(Symbol):
    def __str__(self) -> str:
        return f"<{self.name}:{self.symbol_type}>"

    __repr__ = __str__


class SymbolTable:
    __slots__ = "_symbols"

    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}
        self._init_builtins()

    def __str__(self) -> str:
        return f"Symbols: {[str(val) for val in self._symbols.values()]}"

    def define(self, symbol: Symbol) -> None:
        print(f"Define: {symbol}")
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Symbol | None:
        print(f"Lookup: {name}")
        return self._symbols.get(name)

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol("INTEGER"))
        self.define(BuiltinTypeSymbol("REAL"))
