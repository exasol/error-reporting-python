"""Module defining the internal errors of exasol.error."""

import dataclasses
from dataclasses import dataclass
from inspect import cleandoc
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
)


@dataclass(frozen=True)
class _ExaStaticError:
    identifier: str
    message: str
    messagePlaceholders: List[Dict[str, str]]
    description: Optional[str]
    mitigations: List[str]
    sourceFile: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the static error to a dictionary, excluding "description" if it is None
        """
        ret_val = dataclasses.asdict(self)
        if self.description is None:
            del ret_val["description"]
        return ret_val


# ATTENTION: In the event of an exception while creating an error,
# we encounter a chicken-and-egg problem regarding error definitions.
# Therefore, errors created by this library must be defined
# "statically" within this file.
# Details should then be used to create a low-level error.
# The information should also be used to create/update the error-codes.json
# as part of the release preparation.
# This is only necessary for this library, as it is the root,
# other libraries should use the `ec` command-line tool to update
# and create their project specifc error-codes.json file.
INVALID_ERROR_CODE = _ExaStaticError(
    identifier="E-ERP-1",
    message="Invalid error code {{code}}.",
    messagePlaceholders=[
        {
            "placeholder": "code",
            "description": "Error code which was causing the error.",
        }
    ],
    description=None,
    mitigations=["Ensure you follow the standard error code format."],
    sourceFile=Path(__file__).name,
)

UNKNOWN_EXCEPTION_OCCURED = _ExaStaticError(
    identifier="E-ERP-2",
    message="Unknown error/exception occurred.",
    messagePlaceholders=[
        {
            "placeholder": "traceback",
            "description": "Exception traceback which lead "
            "to the generation of this error.",
        }
    ],
    description="An unexpected error occurred during the creation of the error",
    mitigations=[
        cleandoc(
            """
            A good starting point would be to investigate 
            the cause of the attached exception.

            Trackback:
                {{traceback}}
            """
        )
    ],
    sourceFile=Path(__file__).name,
)

INVALID_ERROR_CODE_DEFINITION = _ExaStaticError(
    identifier="E-ERP-3",
    message="Invalid error code definition: {{error_element}} "
    "only can contain constant values, "
    "but is of type: {{defined_type}}. "
    "In file {{file}} line {{line}}",
    messagePlaceholders=[
        {
            "error_element": "The element within the error "
            "definition which caused the error.",
            "defined_type": "The actual Python type of the error definition.",
            "file": "The file in which the error occurred.",
            "line": "The line where the error occurred.",
        }
    ],
    description="An unexpected error occurred during "
    "the creation of the error catalog, "
    "when parsing the project for EXA error codes.",
    mitigations=[
        cleandoc(
            """
                    Check the definition of ExaError. Possible errors: 
                    1. Usage of none-constant expression in error code, message
                    2. Mitigations are not a list, but another container
                    3. Invalid definition of parameters.

                    """
        )
    ],
    sourceFile=Path(__file__).name,
)

INTERNAL_ERROR_WHEN_CREATING_ERROR_CATALOG = _ExaStaticError(
    identifier="E-ERP-4",
    message="Internal error during creation of the error catalog. "
    "Details to append on Bug ticket: {{traceback}}",
    messagePlaceholders=[
        {
            "traceback": "Traceback which was collected when creating this error.",
        }
    ],
    description="This error signals a programming error in the exasol.error library.",
    mitigations=[
        cleandoc(
            """
                Open a bug ticket at 
                https://github.com/exasol/error-reporting-python/issues/new?template=bug.md
            """
        )
    ],
    sourceFile=Path(__file__).name,
)


LIBRARY_ERRORS = (
    INVALID_ERROR_CODE,
    UNKNOWN_EXCEPTION_OCCURED,
    INVALID_ERROR_CODE_DEFINITION,
    INTERNAL_ERROR_WHEN_CREATING_ERROR_CATALOG,
)
