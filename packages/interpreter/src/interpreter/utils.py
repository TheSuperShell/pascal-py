from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any


class CallStack[T]:
    __slots__ = "_records", "_popped_records"

    def __init__(self) -> None:
        self._records: list[T] = []
        self._popped_records: list[T] = []

    def get_popped_records(self) -> list[T]:
        return self._popped_records

    def pop(self) -> T:
        if len(self._records) == 0:
            raise Exception("stack is empty")

        record = self._records.pop()
        self._popped_records.append(record)
        return record

    def push(self, ar: T) -> None:
        self._records.append(ar)

    def peek(self) -> T:
        if len(self._records) == 0:
            raise Exception("stack is empty")
        return self._records[-1]

    def __str__(self) -> str:
        return f"CALL STACK\n{'\n'.join(repr(ar) for ar in reversed(self._records))}\n"

    def __repr__(self) -> str:
        return str(self)


class ARType(StrEnum):
    PROGRAM = auto()
    PROCEDURE = auto()


@dataclass(slots=True)
class ActivationRecord:
    name: str
    ar_type: ARType
    nesting_level: int
    members: dict[str, Any] = field(default_factory=dict)

    def __setitem__(self, key: str, value: Any) -> None:
        self.members[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.members[key]

    def get(self, key: str) -> Any:
        return self.members.get(key)

    def __str__(self) -> str:
        lines = [f"{self.nesting_level}: {self.ar_type.value} {self.name}"]
        for name, val in self.members.items():
            lines.append(f"    {name:<20}: {val}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return str(self)
