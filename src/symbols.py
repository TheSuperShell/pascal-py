from abc import ABC
from collections.abc import Sequence


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


class ProcedureSymbol(Symbol):
    __slots__ = "name", "params"

    def __init__(self, name: str, params: Sequence[Symbol] | None = None) -> None:
        super().__init__(name)
        self.params: list[Symbol] = list(params) if params is not None else []

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params})>"

    __repr__ = __str__


class ProgramSymbol(Symbol):
    def __init__(self) -> None:
        super().__init__("PROGRAM")

    def __str__(self) -> str:
        return "PROGRAM"

    __repr__ = __str__


class ScopedSymbolTable:
    __slots__ = "_symbols", "scope_name", "scope_level", "enclosing_scope"

    def __init__(
        self,
        scope_name: str,
        *,
        scope_level: int,
        enclosing_sope: "None | ScopedSymbolTable" = None,
    ) -> None:
        self._symbols: dict[str, Symbol] = {}
        self.scope_level = scope_level
        self.scope_name = scope_name
        self.enclosing_scope = enclosing_sope

    def __str__(self) -> str:
        h1 = "SCOPE (SCOPED SYMBOL TABLE)"
        lines = ["\n", h1, "=" * len(h1)]
        for header_name, header_value in (
            ("Scope name", self.scope_name),
            ("Scope level", self.scope_level),
            (
                "Enclosing scope",
                self.enclosing_scope.scope_name if self.enclosing_scope else None,
            ),
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

    def lookup(self, name: str, *, current_scope_only: bool = False) -> Symbol | None:
        print(f"Lookup (scope name: {self.scope_name}): {name}")
        symbol = self._symbols.get(name)
        if symbol is not None:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

    def lookup_with_scope(self, name: str) -> tuple[Symbol | None, int]:
        print(f"Lookup (scope name: {self.scope_name}): {name}")
        symbol = self._symbols.get(name)
        if symbol is not None:
            return symbol, self.scope_level
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup_with_scope(name)
        return None, -1

    @classmethod
    def create_builtin_scope(cls) -> "ScopedSymbolTable":
        print("ENTER scope: builtins")
        table = ScopedSymbolTable("builtins", scope_level=0)
        table.define(BuiltinTypeSymbol("INTEGER"))
        table.define(BuiltinTypeSymbol("REAL"))
        print(table)
        return table
