from abc import ABC


class Symbol(ABC):
    __slots__ = "name", "symbol_type"

    def __init__(self, name: str, symbol_type: "None | Symbol" = None) -> None:
        self.name: str = name
        self.symbol_type: "None | Symbol" = symbol_type

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


class SymbolTable:
    __slots__ = "_symbols"

    def __init__(self) -> None:
        self._symbols: dict[str, Symbol] = {}
        self._init_builtins()

    def __str__(self) -> str:
        header = "Symbol table contents"
        lines = ["\n", header, "_" * len(header)]
        lines.extend(f"{k:>7}: {v}" for k, v in self._symbols.items())
        lines.append("\n")
        return "\n".join(lines)

    def define(self, symbol: Symbol) -> None:
        print(f"Define: {symbol}")
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Symbol | None:
        print(f"Lookup: {name}")
        return self._symbols.get(name)

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol("INTEGER"))
        self.define(BuiltinTypeSymbol("REAL"))
