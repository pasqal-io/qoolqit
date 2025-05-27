from __future__ import annotations

from enum import Enum

ATOL_32 = 1e-07
ATOL_64 = 1e-14


class StrEnum(str, Enum):
    def __str__(self) -> str:
        """Used when dumping enum fields in a schema."""
        ret: str = self.value
        return ret

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))  # type: ignore [attr-defined]
