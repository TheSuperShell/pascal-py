from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Generic, Protocol, TypeVar, override

from parser.parser import AST


class Ref[T](Protocol):
    @property
    def name(self) -> str: ...
    def get(self) -> T | None: ...
    def set(self, val: T) -> None: ...
    def __str__(self) -> str: ...


@dataclass(slots=True)
class VarRef[T]:
    name: str
    value: T | None = None

    def get(self) -> T | None:
        return self.value

    def set(self, val: T) -> None:
        self.value = val

    def __str__(self) -> str:
        return str(self.value)


type PythonTypes = int | str | bool | float | list[PythonTypes | None]


def cast[T](v: PythonTypes | Ref[PythonTypes], expected_type: type[T]) -> T:
    assert isinstance(v, expected_type)
    return v


class SymbolKind(StrEnum):
    VARIABLE = auto()
    CALLABLE = auto()
    TYPE = auto()
    OTHER = auto()


class Symbol(ABC):
    __slots__ = "name", "scope", "kind"

    def __init__(self, name: str, kind: SymbolKind) -> None:
        self.name = name
        self.kind = kind
        self.scope: int = 0

    def set_scope(self, value: int) -> None:
        self.scope = value

    def __str__(self) -> str:
        return f"<{self.kind.name}-{self.__class__.__name__}:{self.name}>"


@dataclass(slots=True, frozen=True)
class FType:
    name: str


T = TypeVar("T", bound=PythonTypes, covariant=True)


class TypeSymbol(Symbol, Generic[T]):
    __slots__ = "f_type", "ordinal_rank", "ordinal_value", "to_string", "indexable"

    def __init__(
        self,
        name: str,
        f_type: FType,
        ordial_rank: Callable[[T], int] | None = None,
        ordinal_value: Callable[[int], T] | None = None,
        to_string: Callable[[T], str] | None = None,
        indexable: bool = False,
    ) -> None:
        super().__init__(name, SymbolKind.TYPE)
        self.f_type = f_type
        self.ordinal_rank = ordial_rank
        self.ordinal_value = ordinal_value
        self.to_string = to_string
        self.indexable = indexable

    @property
    def is_ordinal(self) -> bool:
        return self.ordinal_rank is not None and self.ordinal_value is not None

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TypeSymbol):
            raise
        return self.f_type == value.f_type


class RangeSymbol(Generic[T], TypeSymbol[T]):
    __slots__ = "min_value", "max_value"

    def __init__(
        self, name: str, type_symbol: TypeSymbol[T], min_value: int, max_value: int
    ) -> None:
        super().__init__(
            name,
            type_symbol.f_type,
            type_symbol.ordinal_rank,
            type_symbol.ordinal_value,
            type_symbol.to_string,
            False,
        )
        self.min_value = min_value
        self.max_value = max_value

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TypeSymbol):
            raise
        return self.f_type == value.f_type


class EnumSymbol(TypeSymbol[int]):
    __slots__ = "items"

    def __init__(self, name: str, items: Sequence[str]) -> None:
        super().__init__(
            name, FType("ENUM"), lambda x: x, lambda x: x, lambda x: items[x], False
        )
        self.items: tuple[str, ...] = tuple(items)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, EnumSymbol):
            return False
        return self.items == value.items


In = TypeVar("In", bound=PythonTypes)


class ArraySymbol(Generic[In, T], TypeSymbol[T], ABC):
    __slots__ = "element_type", "index_type"

    def __init__(self, name: str) -> None:
        super().__init__(name, FType("ARRAY"), None, None, str, True)
        self.element_type: TypeSymbol[T]
        self.index_type: TypeSymbol[In]

    @abstractmethod
    def get_index_from_index_value(self, value: In) -> int: ...

    @abstractmethod
    def __eq__(self, value: object) -> bool: ...


class RangedArraySymbol(Generic[In, T], ArraySymbol[In, T]):
    __slots__ = "element_type", "index_type"

    def __init__(
        self, name: str, element_type: TypeSymbol[T], index_type: TypeSymbol[In]
    ) -> None:
        super().__init__(name)
        self.element_type = element_type
        self.index_type = index_type

    def get_index_from_index_value(self, value: In) -> int:
        assert self.index_type.ordinal_rank
        assert isinstance(self.index_type, RangeSymbol)
        value_ord = self.index_type.ordinal_rank(value)
        return value_ord - self.index_type.min_value

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RangedArraySymbol):
            return False
        return (
            self.element_type == value.element_type
            and self.index_type == value.index_type
        )


class DynamicArraySymbol(Generic[T], ArraySymbol[int, T]):
    __slots__ = "element_type", "index_type"

    def __init__(
        self, name: str, element_type: TypeSymbol[T], index_type: TypeSymbol[int]
    ) -> None:
        super().__init__(name)
        self.element_type = element_type
        self.index_type = index_type

    def get_index_from_index_value(self, value: int) -> int:
        return value

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, DynamicArraySymbol):
            return False
        return self.element_type == value.element_type


class VarSymbol(Symbol, Generic[T]):
    __slots__ = "symbol_type"

    def __init__(self, name: str, symbol_type: TypeSymbol[T]) -> None:
        super().__init__(name, SymbolKind.VARIABLE)
        self.symbol_type = symbol_type


class ConstSymbol(Generic[T], Symbol):
    __slots__ = "symbol_type", "value"

    def __init__(self, name: str, symbol_type: TypeSymbol[T], value: T) -> None:
        super().__init__(name, SymbolKind.VARIABLE)
        self.symbol_type = symbol_type
        self.value = value


class ParamMode(StrEnum):
    VALUE = auto()
    REF = auto()


class CallableSymbol(Generic[T], TypeSymbol[T], ABC):
    __slots__ = "return_type", "param_modes", "params"

    def __init__(
        self,
        name: str,
        f_type: FType,
        return_type: TypeSymbol[T] | None = None,
        param_modes: Sequence[ParamMode] | None = None,
        params: Sequence[VarSymbol[PythonTypes]] | None = None,
    ) -> None:
        super().__init__(name, f_type)
        self.kind = SymbolKind.CALLABLE
        self.return_type: TypeSymbol[PythonTypes] | None = return_type
        self.param_modes: list[ParamMode] = (
            list(param_modes) if param_modes is not None else []
        )
        self.params: list[VarSymbol[PythonTypes]] | None = (
            list(params) if params is not None else None
        )


class CustomCallableSymbol(Generic[T], CallableSymbol[T]):
    __slots__ = "block_ast"

    def __init__(
        self,
        name: str,
        return_type: TypeSymbol[T] | None = None,
        param_modes: Sequence[ParamMode] | None = None,
        params: Sequence[VarSymbol[PythonTypes]] | None = None,
        block_ast: AST[Symbol] | None = None,
    ) -> None:
        super().__init__(name, FType("CALLABLE"), return_type, param_modes, params)
        self.block_ast: AST[Symbol] | None = block_ast

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params}, return_type={self.return_type})>"


type BuiltinInput = Sequence[
    tuple[PythonTypes | Ref[PythonTypes], TypeSymbol[PythonTypes] | None]
]


class BuiltinCallableSymbol(Generic[T], CallableSymbol[T]):
    __slots__ = "func"

    def __init__(
        self,
        name: str,
        func: Callable[[BuiltinInput], PythonTypes | None],
        return_type: TypeSymbol[T] | None = None,
        param_modes: Sequence[ParamMode] | None = None,
        params: Sequence[VarSymbol[PythonTypes]] | None = None,
    ) -> None:
        super().__init__(name, FType("CALLABLE"), return_type, param_modes, params)
        self.func: Callable[[BuiltinInput], PythonTypes | None] = func

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={self.params}, return_type={self.return_type})>"


class ProgramSymbol(Symbol):
    def __init__(self, name: str) -> None:
        super().__init__(name, SymbolKind.OTHER)

    @override
    def __str__(self) -> str:
        return "PROGRAM"
