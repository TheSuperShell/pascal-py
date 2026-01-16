from enum import StrEnum, auto
import logging
from interpreter.builtins import BuiltinTypes
from interpreter.symbols import (
    BuiltinCallableSymbol,
    CustomCallableSymbol,
    ConstSymbol,
    Ref,
    Symbol,
    SymbolKind,
    TypeSymbol,
    VarSymbol,
)
from interpreter.builtins import create_builtin_functions
from dataclasses import dataclass, field
from typing import Any


class ARType(StrEnum):
    PROGRAM = auto()
    PROCEDURE = auto()
    FUNCTION = auto()


@dataclass(slots=True)
class ActivationRecord:
    name: str
    ar_type: ARType
    nesting_level: int
    members: dict[str, Ref[Any]] = field(default_factory=dict)

    def __setitem__(self, key: str, value: Ref[Any]) -> None:
        self.members[key.upper()] = value

    def __getitem__(self, key: str) -> Ref[Any]:
        return self.members[key.upper()]

    def __contains__(self, key: str) -> bool:
        return key.upper() in self.members

    def get(self, key: str) -> Ref[Any] | None:
        return self.members.get(key.upper())

    def get_value(self, key: str) -> Any | None:
        if key not in self:
            return None
        return self.members[key.upper()].get()

    def __str__(self) -> str:
        lines = [f"{self.nesting_level}: {self.ar_type.value} {self.name}"]
        for name, val in self.members.items():
            lines.append(f"    {name:<20}: {val}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return str(self)


class CallStack:
    __slots__ = "_records", "_popped_records"

    def __init__(self) -> None:
        self._records: list[ActivationRecord] = []
        self._popped_records: list[ActivationRecord] = []

    def get_popped_records(self) -> list[ActivationRecord]:
        return self._popped_records

    def pop(self) -> ActivationRecord:
        if len(self._records) == 0:
            raise Exception("stack is empty")

        record = self._records.pop()
        self._popped_records.append(record)
        return record

    def push(self, ar: ActivationRecord) -> None:
        self._records.append(ar)

    def peek(self) -> ActivationRecord:
        if len(self._records) == 0:
            raise Exception("stack is empty")
        return self._records[-1]

    def lookup(self, key: str) -> Ref | None:
        for record in reversed(self._records):
            if key in record:
                return record[key]
        return None

    def lookup_value(self, key: str) -> Any | None:
        for record in reversed(self._records):
            if key in record:
                return record[key].get()
        return None

    def __str__(self) -> str:
        return f"CALL STACK\n{'\n'.join(repr(ar) for ar in reversed(self._records))}\n"

    def __repr__(self) -> str:
        return str(self)


class ScopeType(StrEnum):
    BUILTIN = auto()
    PROCEDURE = auto()
    PROGRAM = auto()
    FUNCTION = auto()


class ScopedSymbolTable:
    __slots__ = (
        "_symbols",
        "scope_name",
        "scope_level",
        "enclosing_scope",
        "scope_type",
        "logger",
        "_callable_symbols",
    )

    def __init__(
        self,
        scope_name: str,
        scope_type: ScopeType,
        *,
        scope_level: int,
        logger: logging.Logger,
        enclosing_scope: "None | ScopedSymbolTable" = None,
    ) -> None:
        self._symbols: dict[tuple[str, SymbolKind], Symbol] = {}
        self.scope_level = scope_level
        self.scope_name = scope_name
        self.enclosing_scope = enclosing_scope
        self.scope_type = scope_type
        self.logger = logger

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
        self.logger.debug(f"Define: {symbol}")
        symbol.set_scope(self.scope_level)
        self._symbols[(symbol.name.upper(), symbol.kind)] = symbol

    def lookup(
        self, name: str, kind: SymbolKind, *, current_scope_only: bool = False
    ) -> Symbol | None:
        self.logger.debug(f"Lookup (scope name: {self.scope_name}): {name}")
        name = name.upper()
        symbol = self._symbols.get((name, kind))
        if symbol is not None:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name, kind)
        return None

    def lookup_callable(
        self, name: str, *, current_scope_only: bool = False
    ) -> BuiltinCallableSymbol | CustomCallableSymbol | None:
        result = self.lookup(
            name, SymbolKind.CALLABLE, current_scope_only=current_scope_only
        )
        assert (
            isinstance(result, BuiltinCallableSymbol)
            or isinstance(result, CustomCallableSymbol)
            or result is None
        )
        return result

    def lookup_variable(
        self, name: str, *, current_scope_only: bool = False
    ) -> VarSymbol | ConstSymbol | None:
        result = self.lookup(
            name, SymbolKind.VARIABLE, current_scope_only=current_scope_only
        )
        assert (
            isinstance(result, VarSymbol)
            or isinstance(result, ConstSymbol)
            or result is None
        )
        return result

    def lookup_type(
        self, name: str, *, current_scope_only: bool = False
    ) -> TypeSymbol | None:
        result = self.lookup(
            name, SymbolKind.TYPE, current_scope_only=current_scope_only
        )
        assert isinstance(result, TypeSymbol) or result is None
        return result

    @classmethod
    def create_builtin_scope(cls, logger: logging.Logger) -> "ScopedSymbolTable":
        logger.debug("ENTER scope: builtins")
        table = ScopedSymbolTable(
            "builtins", ScopeType.BUILTIN, scope_level=0, logger=logger
        )
        for t in BuiltinTypes:
            table.define(t.value)
        for f in create_builtin_functions():
            table.define(f)
        logger.debug(table)
        return table
