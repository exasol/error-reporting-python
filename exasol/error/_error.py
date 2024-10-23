import warnings
from dataclasses import dataclass
from inspect import cleandoc
from typing import Dict, Iterable, List, Mapping, Union
from pathlib import Path

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from exasol_error_reporting_python import exa_error


@dataclass(frozen=True)
class Parameter:
    value: str
    description: Union[None, str]


class Error:
    def __init__(
            self,
            code: str,
            message: str,
            mitigations: Union[str, Iterable[str]],
            parameters: Dict[str, Union[str, Parameter]],
    ):
        # This function maybe flattened into or moved out of the constructor in the future.
        def build_error(code, msg, mitigations, params):
            builder = exa_error.ExaError.message_builder(code)
            builder.message(msg)

            for mitigation in mitigations:
                builder.mitigation(mitigation)

            for k, v in params.items():
                name, value, description = k, v, ""
                if isinstance(v, Parameter):
                    value = v.value
                    description = v.description
                builder.parameter(name, value, description)

            return builder

        self._error = build_error(code, message, mitigations, parameters)

    def __str__(self) -> str:
        return f"{self._error}"

    # TODO: Implement __format__ to conveniently support long and short reporting format
    # See also see, Github Issue #28 https://github.com/exasol/error-reporting-python/issues/28


# ATTENTION: In the event of an exception while creating an error, we encounter a chicken-and-egg problem regarding error definitions.
# Therefore, errors created by this library must be defined "statically" within this file.
# Details should then be used to create a low-level error. The information should also be used to create/update the error-codes.json
# as part of the release preparation. This is only necessary for this library, as it is the root, other libraries should use
# the `ec` command-line tool to update and create their project specifc error-codes.json file.
LIBRARY_ERRORS = {
    "E-ERP-1": {
        "identifier": "E-ERP-1",
        "message": "Invalid error code {{code}}.",
        "messagePlaceholders": [
            {
                "placeholder": "code",
                "description": "Error code which was causing the error."
            }
        ],
        "mitigations": ["Ensure you follow the standard error code format."],
        "sourceFile": Path(__file__).name
    },
    "E-ERP-2": {
        "identifier": "E-ERP-2",
        "message": "Unknown error/exception occurred.",
        "messagePlaceholders": [
            {
                "placeholder": "traceback",
                "description": "Exception traceback which lead to the generation of this error."
            }
        ],
        "description": "An unexpected error occurred during the creation of the error",
        "mitigations": [cleandoc("""
                    A good starting point would be to investigate the cause of the attached exception.
        
                    Trackback:
                        {{traceback}}
                    """)],
        "sourceFile": Path(__file__).name
    },
}


def ExaError(
        code: str,
        message: str,
        mitigations: Union[str, List[str]],
        parameters: Mapping[str, Union[str, Parameter]],
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
    except ValueError:
        error_code = 'E-ERP-1'
        error_details = LIBRARY_ERRORS[error_code]
        return Error(
            code=error_details['identifier'],
            message=error_details['message'],
            mitigations=error_details['mitigations'],
            parameters={"code": code}
        )
    except Exception as ex:
        import traceback
        tb = traceback.format_exc()
        parameters = {"traceback": tb}
        error_code = 'E-ERP-2'
        error_details = LIBRARY_ERRORS[error_code]
        return Error(
            code=error_details['identifier'],
            message=error_details['message'],
            mitigations=error_details['mitigations'],
            parameters=parameters
        )


def _create_error_code_definitions(version=None):
    from exasol.error.version import VERSION
    version = version or VERSION
    return {
        "$schema": "https://schemas.exasol.com/error_code_report-1.0.0.json",
        "projectName": "exasol-error-reporting",
        "projectVersion": version,
        "errorCodes": [code for code in LIBRARY_ERRORS.values()]
    }


if __name__ == "__main__":
    pass
