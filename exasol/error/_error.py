import warnings
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Dict, List, Union

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
        name: str,
        message: str,
        mitigations: Union[str, Iterable[str]],
        parameters: Dict[str, Union[str, Parameter]],
    ):
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

        self._error = build_error(name, message, mitigations, parameters)

    def __str__(self) -> str:
        return f"{self._error}"

    # TODO: Implement __format__ to conveniently support long and short reporting format


def ExaError(
    name: str,
    message: str,
    mitigations: Union[str, List[str]],
    parameters: Mapping[str, Union[str, Parameter]],
) -> Error:
    """Create a new ExaError.

    The caller is responsible to make sure that the chosen name/id is unique.

    Args:
        name: unique name/id of the error.
        message: the error message itself. It can contain placeholders for parameters.
        mitigations: One or multiple mitigations strings. A mitigation can contain placeholders for parameters.
        parameters: which will be used for substitute the parameters in the mitigation(s) and the error message.


    Returns:
        An error type containing all relevant information.


    Raises:
        This function should not raise under any circumstances.
        In case of error, it should report it also as an error type which is returned by this function.
        Still the returned error should contain a references or information about the original call.

        Attention:

            FIXME: Due to legacy reasons this function currently still may raise an `ValueError` (Refactoring Required).

            Potential error scenarios which should taken into account are the following ones:
             * ExaError('E-ERP-1', 'Invalid error code provided.', [], []),
             * ExaError('E-ERP-2', 'Invalid parameter specification.', [], []),
             * ExaError('E-ERP-3', 'Invalid error message specification.', [], []),
             * ExaError('E-ERP-4', 'Invalid mitigation specification.', [], []),
    """
    return Error(name, message, mitigations, parameters)
