import re
from typing import Any
from exasol_error_reporting_python.parameters_mapper import ParametersMapper
from exasol_error_reporting_python.placeholder_handler import PlaceholderHandler

ERROR_CODE_FORMAT = "^[FEW]-[A-Z][A-Z0-9]+(-[A-Z][A-Z0-9]+)*-[0-9]+$"


class InvalidErrorCode(Exception):
    """
    Indicates that the error code does not comply with the commonly defined error code format.
    """


class ErrorMessageBuilder:
    """
    This class is a builder for Exasol error messages.
    """

    def __init__(self, error_code: str):
        if not re.compile(ERROR_CODE_FORMAT).match(error_code):
            raise InvalidErrorCode(f"{error_code} is an invalid error-code format")

        self._error_code = error_code
        self._message_builder = []
        self._mitigations = []
        self._parameter_dict = {}

    def message(self, message: str, *arguments):
        """
        Add the given error message to the error builder list and invokes
        the method that performs mapping of the given parameters with the
        placeholders in the message. This class allows multiple calls for
        message or mitigation methods, in this case the text given in
        message or mitigation is appended to the list of the corresponding
        method.

        :param message: an error message that may contain placeholders
        :param arguments: a tuple of parameters to replace with the placeholders

        :return: self of the ErrorMessageBuilder object
        """

        self._message_builder.append(message)
        self._add_parameters(message, arguments)
        return self

    def mitigation(self, mitigation: str, *arguments):
        """
        Add the given mitigation message, explaining  what users can do to
        resolve or avoid this error, to the mitigation list and invokes
        the method that perform mapping of the given parameters with the
        placeholders in the mitigation message.

        :param mitigation: a mitigation message that may contain placeholders
        :param arguments: a tuple of parameters to replace with the placeholders

        :return: self of the ErrorMessageBuilder object
        """

        self._mitigations.append(mitigation)
        self._add_parameters(mitigation, arguments)
        return self

    def ticket_mitigation(self):
        """
        Add a pre-defined mitigation message  for cases where the only thing
        a user can do is opening a ticket.

        :return: self of the ErrorMessageBuilder object
        """

        self.mitigation(
            "This is an internal error that should not happen. "
            "Please report it by opening a GitHub issue."
        )
        return self

    def parameter(self, placeholder: str, value: Any, description: str = None):
        """
        Keep the given placeholder with the given parameter in a dictionary.
        This function can be used for any placeholder in message and mitigation.

        :param placeholder: name of the placeholder
        :param value: value corresponding to placeholder
        :param description: description for the error catalog

        :return: self of the ErrorMessageBuilder object
        """

        self._parameter_dict[placeholder] = value
        return self

    def _add_parameters(self, text: str, arguments: Any):
        """
        Maps placeholders in the given text with positional arguments.
        Placeholders are defined in the text by using double curly brackets
        such as '{{argument_name}}'.

        :param text: message or mitigation that may contain placeholders
        :param arguments: arguments to replace with  the placeholders
        """

        arguments = list(arguments) if arguments else []

        self._parameter_dict = {
            **self._parameter_dict,
            **ParametersMapper.get_params_dict(text, arguments),
        }

    def _replace_placeholder(self, text: str) -> str:
        """
        Replace placeholders with the arguments.

        :param text: message or mitigation that may contain placeholders
        :return: formatted text by replacing placeholders with arguments.
        """

        return PlaceholderHandler.replace_placeholder(text, self._parameter_dict)

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
                mitigations.append(
                    "".join(("* ", self._replace_placeholder(mitigation)))
                )
            result.append("\n".join(mitigations))

        return " ".join(result)
