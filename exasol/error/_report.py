import json
from dataclasses import (
    asdict,
    dataclass,
    is_dataclass,
)
from typing import (
    List,
    Optional,
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
    description: Optional[str]


@dataclass
class ErrorCodeDetails:
    """
    Error code details according to schema specification.
    https://schemas.exasol.com/error_code_report-1.0.0.json
    """

    identifier: str
    message: Optional[str]
    messagePlaceholders: Optional[list[Placeholder]]
    description: Optional[str]
    internalDescription: Optional[str]
    potentialCauses: Optional[list[str]]
    mitigations: Optional[list[str]]
    sourceFile: Optional[str]
    sourceLine: Optional[int]
    contextHash: Optional[str]
