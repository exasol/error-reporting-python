import re
from typing import Any

from exasol_error_reporting_python.parameters_mapper import ParametersMapper
from exasol_error_reporting_python.placeholder_handler import PlaceholderHandler

ERROR_CODE_FORMAT = "^[FEW]-[[A-Z][A-Z0-9]+(-[A-Z][A-Z0-9]+)*-[0-9]+$"


class ErrorMessageBuilder:
    def __init__(self, error_code: str):
        assert re.compile(ERROR_CODE_FORMAT).match(error_code)

        self._error_code = error_code
        self._message_builder = []
        self._mitigations = []
        self._parameter_dict = {}

    def message(self, message: str, *arguments):
        self._message_builder.append(message)
        self._add_parameters(message, arguments)
        return self

    def mitigation(self, mitigation: str, *arguments):
        self._mitigations.append(mitigation)
        self._add_parameters(mitigation, arguments)
        return self

    def ticket_mitigation(self):
        self.mitigation("This is an internal error that should not happen. "
                        "Please report it by opening a GitHub issue.")
        return self

    def parameter(self, placeholder: str, value: Any, description: str = None):
        self._parameter_dict[placeholder] = value
        return self

    def _add_parameters(self, text: str, arguments: Any):
        arguments = list(arguments) if arguments else []

        self._parameter_dict = {
            **self._parameter_dict,
            **ParametersMapper.get_params_dict(text, arguments)
        }

    def _replace_placeholder(self, text: str) -> str:
        return PlaceholderHandler.replace_placeholder(
            text, self._parameter_dict)

    def __str__(self):
        result = []

        if self._message_builder:
            result.append(f"{self._error_code}:")
            result += [self._replace_placeholder("".join(self._message_builder))]
        else:
            result.append(self._error_code)

        if len(self._mitigations) == 1:
            result.append(self._replace_placeholder(self._mitigations[0]))
        elif len(self._mitigations) > 1:
            mitigations = ["Known mitigations:"]
            for mitigation in self._mitigations:
                mitigations.append("".join(
                    ("* ", self._replace_placeholder(mitigation))))
            result.append("\n".join(mitigations))

        return " ".join(result)

