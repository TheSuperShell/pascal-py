from dataclasses import dataclass, field
from enum import StrEnum, auto
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
    members: dict[str, Any] = field(default_factory=dict)

    def __setitem__(self, key: str, value: Any) -> None:
        self.members[key.upper()] = value

    def __getitem__(self, key: str) -> Any:
        return self.members[key.upper()]

    def __contains__(self, key: str) -> bool:
        return key.upper() in self.members

    def get(self, key: str) -> Any:
        return self.members.get(key.upper())

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

    def lookup(self, key: str) -> ActivationRecord | None:
        for record in reversed(self._records):
            if key in record:
                return record[key]
        return None

    def __str__(self) -> str:
        return f"CALL STACK\n{'\n'.join(repr(ar) for ar in reversed(self._records))}\n"

    def __repr__(self) -> str:
        return str(self)
