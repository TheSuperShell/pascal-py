from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
import inspect
from interpreter.symbols import BuiltinCallableSymbol, TypeSymbol, VarSymbol


class BuiltinTypes(Enum):
    INTEGER = TypeSymbol[int]("INTEGER", 0, lambda x: x, lambda x: x)
    REAL = TypeSymbol[float]("REAL", 0)
    BOOLEAN = TypeSymbol[bool]("BOOLEAN", 0)
    CHAR = TypeSymbol[str]("CHAR", 0, ord, chr)
    STRING = TypeSymbol[str]("STRING", 0)

    @classmethod
    def get_pascal_type_from_python_type(
        cls, python_type: type[object]
    ) -> "BuiltinTypes":
        if python_type is int:
            return cls.INTEGER
        if python_type is float:
            return cls.REAL
        if python_type is bool:
            return cls.BOOLEAN
        if python_type is str:
            return cls.STRING
        raise ValueError(f"unsupported type {python_type}")


@dataclass(slots=True)
class BuiltinFunctionRegister:
    registered_functions: list[BuiltinCallableSymbol] = field(default_factory=list)

    def register_function[**P, R](
        self, symbol_name: str | None = None
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def wrapper(func: Callable[P, R]) -> Callable[P, R]:
            sign = inspect.signature(func)
            return_type = sign.return_annotation
            return_type = (
                return_type if sign.return_annotation != inspect._empty else None
            )
            return_symbol = (
                BuiltinTypes.get_pascal_type_from_python_type(return_type).value
                if return_type is not None
                else None
            )
            params = sign.parameters
            param_symbols: list[VarSymbol] | None = []
            for name, param in params.items():
                if param.kind == inspect._ParameterKind.VAR_POSITIONAL:
                    assert len(params) == 1, (
                        f"only one input parameter is allowed when using *args: {func.__name__}"
                    )
                    param_symbols = None
                    break
                if param.kind not in (
                    inspect._ParameterKind.POSITIONAL_OR_KEYWORD,
                    inspect._ParameterKind.POSITIONAL_ONLY,
                ):
                    raise NotImplementedError(
                        "only positional or *args parameters are implemeneted"
                        f" for builtin functions: {param.kind}"
                    )
                param_type = param.annotation
                assert param_type != inspect._empty, (
                    "all builtin function parameters should be annotated"
                )
                assert param_symbols is not None
                param_symbols.append(
                    VarSymbol(
                        name,
                        0,
                        BuiltinTypes.get_pascal_type_from_python_type(param_type).value,
                    )
                )
            self.registered_functions.append(
                BuiltinCallableSymbol(
                    symbol_name if symbol_name is not None else func.__name__,
                    0,
                    func,
                    param_symbols,
                    return_symbol,
                )
            )
            return func

        return wrapper


builtin_function_register = BuiltinFunctionRegister()


@builtin_function_register.register_function()
def writeln(*args: object) -> None:
    print(*args, sep="")


@builtin_function_register.register_function()
def write(*args: object) -> None:
    print(*args, end="")


@builtin_function_register.register_function()
def length(text: str) -> int:
    return len(text)
