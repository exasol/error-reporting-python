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

    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)


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
    messagePlaceholders: Optional[List[Placeholder]]
    description: Optional[str]
    internalDescription: Optional[str]
    potentialCauses: Optional[List[str]]
    mitigations: Optional[List[str]]
    sourceFile: Optional[str]
    sourceLine: Optional[int]
    contextHash: Optional[str]
