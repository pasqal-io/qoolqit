from __future__ import annotations

from enum import Enum, EnumMeta

ATOL_32 = 1e-07
ATOL_64 = 1e-14


class CustomEnumMeta(EnumMeta):
    def __repr__(cls):
        members = "\n| ".join([f"{member.name} = {repr(member.value)}" for member in cls])
        return f"<Enum '{cls.__name__}':\n| {members}>"


class StrEnum(str, Enum, metaclass=CustomEnumMeta):
    def __str__(self) -> str:
        """Used when dumping enum fields in a schema."""
        ret: str = self.value
        return ret

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))  # type: ignore [attr-defined]
