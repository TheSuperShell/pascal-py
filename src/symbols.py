from abc import ABC


class Symbol(ABC):
    __slots__ = "name", "symbol_type"

    def __init__(self, name: str, symbol_type: "None | Symbol" = None) -> None:
        self.name: str = name
        self.symbol_type: "None | Symbol" = symbol_type

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}'" + (
            f", type='{self.symbol_type.name}')>" if self.symbol_type else ")>"
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


class ProcedureSymbol(Symbol):
    __slots__ = "name", "params"

    def __init__(self, name: str, params: list[Symbol] | None = None) -> None:
        super().__init__(name)
        self.params: list[Symbol] = params if params is not None else []

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__}(name={self.name}, parameters={self.params})>"
        )

    __repr__ = __str__


class ScopedSymbolTable:
    __slots__ = "_symbols", "scope_name", "scope_level"

    def __init__(self, scope_name: str, *, scope_level: int) -> None:
        self._symbols: dict[str, Symbol] = {}
        self.scope_level = scope_level
        self.scope_name = scope_name
        self._init_builtins()

    def __str__(self) -> str:
        h1 = "SCOPE (SCOPED SYMBOL TABLE)"
        lines = ["\n", h1, "=" * len(h1)]
        for header_name, header_value in (
            ("Scope name", self.scope_name),
            ("Scope level", self.scope_level),
        ):
            lines.append(f"{header_name:<15}: {header_value}")
        h2 = "Scope (Scoped symbol table) contents"
        lines.extend([h2, "-" * len(h2)])
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
