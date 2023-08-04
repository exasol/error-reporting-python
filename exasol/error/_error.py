import dataclasses
import warnings
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Union

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from exasol_error_reporting_python import exa_error


def _to_iterable(value):
    if isinstance(value, Iterable):
        return value
    return [value]


@dataclass(frozen=True)
class Parameter:
    name: str
    value: str
    description: Union[None, str]


class Error:
    def __init__(self, name, message, mitigations, parameters):
        def build_error(code, msg, mitigations, params):
            builder = exa_error.ExaError.message_builder(code)
            builder.message(msg)
            for mitigation in mitigations:
                builder.mitigation(mitigation)
            if isinstance(params, dict):
                for k, v in params.items():
                    builder.parameter(k, v, "")
            else:
                for parameter in params:
                    if isinstance(parameter, Parameter):
                        parameter = dataclasses.asdict(parameter)
                    builder.parameter(*parameter.values())
            return builder

        # treat single values also as iterable
        mitigations = _to_iterable(mitigations)
        parameters = _to_iterable(parameters)

        self._error = build_error(name, message, mitigations, parameters)

    def __str__(self) -> str:
        return f"{self._error}"

    # TODO: Implement __format__ to conveniently support long and short reporting format


def ExaError(
    name: str,
    message: str,
    mitigations: Union[str, Iterable[str]],
    parameters: Union[Parameter, Mapping[str, str], Iterable[Parameter]],
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
        In case of error it should report it also as an error type which is returned by this function.
        Still the returned error should contain a references or information about the original call.

        Attention:

            FIXME: Due to legacy reasons this function currently still may raise an `ValueError` (Refactoring Required).

            Potential error scenarios which should taken into account are the following ones:
             * ExaError('ERP-1', 'Invalid error code provided.', [], []),
             * ExaError('ERP-2', 'Invalid parameter specification.', [], []),
             * ExaError('ERP-3', 'Invalid error message specification.', [], []),
             * ExaError('ERP-4', 'Invalid mitigation specification.', [], []),
    """
    return Error(name, message, mitigations, parameters)
