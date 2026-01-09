from enum import StrEnum, auto
from parser.parser import BuiltinCallableSymbol, BuiltinTypeSymbol, Symbol


class ScopeType(StrEnum):
    BUILTIN = auto()
    PROCEDURE = auto()
    PROGRAM = auto()
    FUNCTION = auto()


class ScopedSymbolTable:
    __slots__ = "_symbols", "scope_name", "scope_level", "enclosing_scope", "scope_type"

    def __init__(
        self,
        scope_name: str,
        scope_type: ScopeType,
        *,
        scope_level: int,
        enclosing_sope: "None | ScopedSymbolTable" = None,
    ) -> None:
        self._symbols: dict[str, Symbol] = {}
        self.scope_level = scope_level
        self.scope_name = scope_name
        self.enclosing_scope = enclosing_sope
        self.scope_type = scope_type

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
        symbol.scope = self.scope_level
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
        table = ScopedSymbolTable("builtins", ScopeType.BUILTIN, scope_level=0)
        table.define(BuiltinTypeSymbol("INTEGER"))
        table.define(BuiltinTypeSymbol("REAL"))
        table.define(BuiltinTypeSymbol("BOOLEAN"))
        table.define(BuiltinCallableSymbol("WriteLn", print))
        print(table)
        return table
