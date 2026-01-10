from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any, override

from parser.parser import AST


class SymbolKind(StrEnum):
    VARIABLE = auto()
    CALLABLE = auto()
    TYPE = auto()
    OTHER = auto()


@dataclass(slots=True)
class Symbol(ABC):
    name: str
    scope: int

    @property
    @abstractmethod
    def kind(self) -> SymbolKind: ...

    def __str__(self) -> str:
        return f"<{self.kind.name}:{self.name}>"


@dataclass(slots=True, frozen=True)
class FType:
    name: str


@dataclass(slots=True)
class TypeSymbol[T](Symbol):
    f_type: FType
    ordinal_rank: Callable[[T], int] | None = None
    ordinal_value: Callable[[int], T] | None = None

    @property
    @override
    def kind(self) -> SymbolKind:
        return SymbolKind.TYPE

    @property
    def is_ordinal(self) -> bool:
        return self.ordinal_rank is not None and self.ordinal_value is not None

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TypeSymbol):
            return False
        return self.f_type == value.f_type


@dataclass(slots=True)
class VarSymbol(Symbol):
    symbol_type: TypeSymbol

    @property
    @override
    def kind(self) -> SymbolKind:
        return SymbolKind.VARIABLE


@dataclass(slots=True)
class CallableSymbol(Symbol):
    return_type: TypeSymbol | None = None
    params: list[VarSymbol] = field(default_factory=list)
    block_ast: AST | None = None

    @property
    @override
    def kind(self) -> SymbolKind:
        return SymbolKind.CALLABLE

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params}, return_type={self.return_type})>"


@dataclass(slots=True)
class BuiltinCallableSymbol(Symbol):
    func: Callable[..., Any]
    params: list[VarSymbol] | None = None
    return_type: TypeSymbol | None = None

    @property
    @override
    def kind(self) -> SymbolKind:
        return SymbolKind.CALLABLE

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params}, return_type={self.return_type})>"


@dataclass(slots=True)
class ProgramSymbol(Symbol):
    @property
    @override
    def kind(self) -> SymbolKind:
        return SymbolKind.OTHER

    @override
    def __str__(self) -> str:
        return "PROGRAM"
