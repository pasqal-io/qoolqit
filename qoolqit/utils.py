from __future__ import annotations

from enum import Enum, EnumMeta

ATOL_32 = 1e-07
ATOL_64 = 1e-14


class CustomEnumMeta(EnumMeta):
    def __repr__(cls) -> str:
        members = "\n| ".join(
            [f"{m.name} = {repr(m.value)}" for m in cls]  # type: ignore [var-annotated]
        )
        return f"<Enum '{cls.__name__}':\n| {members}>"


class StrEnum(str, Enum, metaclass=CustomEnumMeta):
    def __str__(self) -> str:
        """Used when dumping enum fields in a schema."""
        ret: str = self.value
        return ret

    @classmethod
    def list(cls, values: bool = False) -> list:
        if values:
            return [item.value for item in cls]
        else:
            return [item for item in cls]
