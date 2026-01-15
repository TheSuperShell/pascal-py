from enum import Enum
from typing import Any, Protocol
from interpreter.symbols import (
    BuiltinCallableSymbol,
    BuiltinInput,
    FType,
    ParamMode,
    Symbol,
    TypeSymbol,
    VarSymbol,
)
from parser.parser import Literal
from parser.token import TokenType


class BuiltinTypes(Enum):
    INTEGER = TypeSymbol[int](
        "INTEGER", 0, FType("INTEGER"), lambda x: x, lambda x: x, str
    )
    REAL = TypeSymbol[float]("REAL", 0, FType("REAL"), None, None, str)
    BOOLEAN = TypeSymbol[bool]("BOOLEAN", 0, FType("BOOLEAN"), int, bool, str)
    CHAR = TypeSymbol[str]("CHAR", 0, FType("CHAR"), ord, chr, lambda x: x)
    STRING = TypeSymbol[str]("STRING", 0, FType("STRING"), None, None, lambda x: x)

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


def create_builtin_functions(io: IO = StdIO()) -> list[BuiltinCallableSymbol]:
    def write(args: BuiltinInput) -> None:
        for val, val_type in args:
            to_string = val_type.to_string if val_type and val_type.to_string else str
            io.write(to_string(val))

    def writeln(args: BuiltinInput, end: str = "\n") -> None:
        write(args)
        io.write("\n")

    def readln(args: BuiltinInput) -> None:
        args[0][0].set(io.read())

    result = []
    result.append(
        BuiltinCallableSymbol("writeln", 0, writeln, [ParamMode.VALUE], None, None)
    )
    result.append(BuiltinCallableSymbol("write", 0, write, [ParamMode.VALUE], None))
    result.append(
        BuiltinCallableSymbol(
            "readln",
            0,
            readln,
            [ParamMode.REF],
            [VarSymbol("inp_var", 0, BuiltinTypes.STRING.value)],
        )
    )
    result.append(
        BuiltinCallableSymbol(
            "length",
            0,
            length,
            [ParamMode.VALUE],
            [VarSymbol("text", 0, BuiltinTypes.STRING.value)],
            BuiltinTypes.INTEGER.value,
        )
    )
    return result


def length(args: BuiltinInput) -> int:
    text = args[0][0]
    return len(text)
