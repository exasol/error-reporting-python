from collections.abc import Iterable
from dataclasses import dataclass
from typing import (
    Any,
)

from exasol.error import _exa_error
from exasol.error._error_message_builder import (
    InvalidErrorCode,
)
from exasol.error._internal_errors import (
    INVALID_ERROR_CODE,
    LIBRARY_ERRORS,
    UNKNOWN_EXCEPTION_OCCURED,
)


@dataclass(frozen=True)
class Parameter:
    value: str
    description: None | str


class Error:
    def __init__(
        self,
        code: str,
        message: str,
        mitigations: str | Iterable[str],
        parameters: dict[str, str | Parameter],
    ) -> None:
        builder = _exa_error.ExaError.message_builder(code)
        builder.message(message)

        for mitigation in mitigations:
            builder.mitigation(mitigation)

        for k, v in parameters.items():
            name = k
            value = v
            description: str | None = ""
            if isinstance(v, Parameter):
                value = v.value
                description = v.description
            builder.parameter(name, value, description)

        self._error = builder

    def __str__(self) -> str:
        return f"{self._error}"

    def __format__(self, format_spec: str):
        def _name(error: Error):
            return f"{error._error._error_code} "

        def _message(error: Error):
            return f"{error._error._message_builder} "

        def _mitigations(error: Error):
            return f"{error._error._mitigations} "

        def _parameters(error: Error):
            return f"{error._error._parameter_dict} "

        def _short(error: Error):
            return _name(error) + _message(error)

        def _long(error: Error):
            return (
                _name(error)
                + _message(error)
                + _mitigations(error)
                + _parameters(error)
            )

        output = ""
        formats = {
            "name": _name(self),
            "message": _message(self),
            "mitigations": _mitigations(self),
            "parameters": _parameters(self),
            "short": _short(self),
            "long": _long(self),
            "": "",
        }
        for part in format_spec.split(" "):
            if part in formats:
                output += formats[part]

        return output[:-1]


def ExaError(
    code: str,
    message: str,
    mitigations: str | list[str],
    parameters: dict[str, str | Parameter],
) -> Error:
    """Create a new ExaError.

    The caller is responsible to make sure that the chosen code/id is unique.

    Args:
        code: unique name/id of the error.
        message: the error message itself. It can contain placeholders for parameters.
        mitigations: One or multiple mitigations strings. A mitigation can contain placeholders for parameters.
        parameters: which will be used for substitute the parameters in the mitigation(s) and the error message.


    Returns:
        An error type containing all relevant information.
    """
    try:
        return Error(code, message, mitigations, parameters)
    except InvalidErrorCode:
        return Error(
            code=INVALID_ERROR_CODE.identifier,
            message=INVALID_ERROR_CODE.message,
            mitigations=INVALID_ERROR_CODE.mitigations,
            parameters={"code": code},
        )
    except Exception as ex:
        import traceback

        tb = traceback.format_exc()
        parameters = {"traceback": tb}
        return Error(
            code=UNKNOWN_EXCEPTION_OCCURED.identifier,
            message=UNKNOWN_EXCEPTION_OCCURED.message,
            mitigations=UNKNOWN_EXCEPTION_OCCURED.mitigations,
            parameters=parameters,
        )


def _create_error_code_definitions(version=None) -> dict[str, Any]:
    from exasol.error.version import VERSION

    version = version or VERSION
    return {
        "$schema": "https://schemas.exasol.com/error_code_report-1.0.0.json",
        "projectName": "exasol-error-reporting",
        "projectVersion": version,
        "errorCodes": [code.to_dict() for code in list(LIBRARY_ERRORS)],
    }


if __name__ == "__main__":
    pass
