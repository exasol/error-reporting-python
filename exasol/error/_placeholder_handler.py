import re
from collections.abc import Iterable
from typing import (
    Any,
)

from exasol.error._placeholder import Placeholder


class PlaceholderHandler:
    """
    This class is responsible for handling Placeholder operations such as
    extracting placeholder, replacing placeholders with the corresponding
    parameters, handling quotation of placeholder.
    """

    PLACEHOLDER_PATTERN = "{{([^}]*)}}"
    PLACEHOLDER_NONE = "<null>"

    @classmethod
    def get_placeholders(cls, text: str) -> Iterable[Placeholder]:
        """
        Parse the given text and find placeholders.

        :param text: message or mitigation that may contain placeholders

        :return: yields a generator  holding Placeholder objects
        """

        for match in re.finditer(cls.PLACEHOLDER_PATTERN, text):
            yield Placeholder(key=match.group(0), text=match.group(1))

    @classmethod
    def replace_placeholder(cls, text: str, parameter_dict: dict) -> str:
        """
        Replace the placeholders, if any, of the given text with
        the corresponding parameters.

        :param text: message or mitigation that may contain placeholders
        :param parameter_dict:

        :return: text with its placeholders replaced
        """

        for placeholder in cls.get_placeholders(text):
            replacement = cls.get_parameter_from_dict(placeholder, parameter_dict)
            text = text.replace(placeholder.key, replacement)
        return text

    @classmethod
    def get_parameter_from_dict(
        cls, placeholder: Placeholder, parameter_dict: dict
    ) -> Any:
        """
        Return parameter for the given placeholder, if any, considering
        whether the parameter will be quoted or not. Otherwise, returns <null>.

        :param placeholder: a Placeholder object
        :param parameter_dict: a dictionary holding placeholders and parameters

        :return: parameter value if exists, otherwise <null>
        """

        parameter = parameter_dict.get(placeholder.name, None)

        if parameter is None:
            return cls.PLACEHOLDER_NONE
        if cls.is_unquoted_param(placeholder, parameter):
            return str(parameter)
        else:
            return f"'{parameter}'"

    @classmethod
    def is_unquoted_param(cls, placeholder: Placeholder, parameter: Any):
        """
        Checks whether the given parameter needs quotation or not.

        :param placeholder: a Placeholder object
        :param parameter: a parameter value

        :return: True if the given parameter will not be quoted.
        """
        return placeholder.is_unquoted() or not isinstance(parameter, str)
