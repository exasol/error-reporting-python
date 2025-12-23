import json
from dataclasses import (
    asdict,
    dataclass,
    is_dataclass,
)


class JsonEncoder(json.JSONEncoder):
    """Json encoder with dataclass support"""

    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


@dataclass(frozen=True)
class Placeholder:
    """
    Placeholder according to schema specification.
    https://schemas.exasol.com/error_code_report-1.0.0.json
    """

    placeholder: str
    description: str | None


@dataclass
class ErrorCodeDetails:
    """
    Error code details according to schema specification.
    https://schemas.exasol.com/error_code_report-1.0.0.json
    """

    identifier: str
    message: str | None
    messagePlaceholders: list[Placeholder] | None
    description: str | None
    internalDescription: str | None
    potentialCauses: list[str] | None
    mitigations: list[str] | None
    sourceFile: str | None
    sourceLine: int | None
    contextHash: str | None
