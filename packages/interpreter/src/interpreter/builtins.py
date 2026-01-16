from enum import Enum
from typing import Any, Protocol
from interpreter.symbols import (
    BuiltinCallableSymbol,
    BuiltinInput,
    FType,
    ParamMode,
    PythonTypes,
    Symbol,
    TypeSymbol,
    VarSymbol,
    cast,
)
from interpreter.symbols import VarRef
from parser.parser import Literal
from parser.token import TokenType


class BuiltinTypes(Enum):
    INTEGER = TypeSymbol[int](
        "INTEGER", FType("INTEGER"), lambda x: x, lambda x: x, str
    )
    REAL = TypeSymbol[float]("REAL", FType("REAL"), None, None, str)
    BOOLEAN = TypeSymbol[bool]("BOOLEAN", FType("BOOLEAN"), int, bool, str)
    CHAR = TypeSymbol[str]("CHAR", FType("CHAR"), ord, chr, lambda x: x)
    STRING = TypeSymbol[str]("STRING", FType("STRING"), None, None, lambda x: x)

    @classmethod
    def literal_to_builtin(cls, literal: Literal[Any, Symbol]) -> "BuiltinTypes":
        match literal.token.token_type:
            case TokenType.CHAR_CONST:
                return cls.CHAR
            case TokenType.STRING_CONST:
                return cls.STRING
            case TokenType.BOOLEAN_CONST:
                return cls.BOOLEAN
            case TokenType.INTEGER_CONST:
                return cls.INTEGER
            case TokenType.REAL_CONST:
                return cls.REAL
        raise ValueError(f"unsupported literal {literal}")

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


class IO(Protocol):
    def read(self) -> str:
        """read the input of the program

        Returns:
            str: input
        """
        ...

    def write(self, value: str) -> None:
        """write to the output of the program

        Args:
            value (str): output
        """
        ...


class StdIO:
    def read(self) -> str:
        return input()

    def write(self, value: str) -> None:
        print(value, sep="", end="")


def create_builtin_functions(
    io: IO = StdIO(),
) -> list[BuiltinCallableSymbol[PythonTypes]]:
    def write(args: BuiltinInput) -> None:
        for val, val_type in args:
            to_string = val_type.to_string if val_type and val_type.to_string else str
            io.write(to_string(val))  # type: ignore

    def writeln(args: BuiltinInput) -> None:
        write(args)
        io.write("\n")

    def readln(args: BuiltinInput) -> None:
        cast(args[0][0], VarRef).set(io.read())

    result: list[BuiltinCallableSymbol[PythonTypes]] = []
    result.append(
        BuiltinCallableSymbol("writeln", writeln, None, [ParamMode.VALUE], None)
    )
    result.append(BuiltinCallableSymbol("write", write, None, [ParamMode.VALUE]))
    result.append(
        BuiltinCallableSymbol(
            "readln",
            readln,
            None,
            [ParamMode.REF],
            [VarSymbol("inp_var", BuiltinTypes.STRING.value)],
        )
    )
    result.append(
        BuiltinCallableSymbol(
            "length",
            length,
            BuiltinTypes.INTEGER.value,
            [ParamMode.VALUE],
            [VarSymbol("text", BuiltinTypes.STRING.value)],
        )
    )
    result.append(
        BuiltinCallableSymbol(
            "setlength", setlength, None, [ParamMode.REF, ParamMode.VALUE]
        )
    )
    return result


def length(args: BuiltinInput) -> int:
    return len(cast(args[0][0], str))


def setlength(args: BuiltinInput) -> None:
    arr = cast(args[0][0], VarRef)
    size = cast(args[1][0], int)
    arr.set([None for _ in range(size)])
