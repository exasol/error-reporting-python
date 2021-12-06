import re
from typing import Any, Iterable

from exasol_error_reporting_python.placeholder import Placeholder


class PlaceholderHandler:
    PLACEHOLDER_PATTERN = "{{([^}]*)}}"
    PLACEHOLDER_NONE = "<null>"

    @classmethod
    def get_placeholders(cls, text: str) -> Iterable[Placeholder]:
        for match in re.finditer(cls.PLACEHOLDER_PATTERN, text):
            yield Placeholder(
                key=match.group(0),
                text=match.group(1))

    @classmethod
    def replace_placeholder(cls, text: str, parameter_dict: dict) -> str:
        for placeholder in cls.get_placeholders(text):
            replacement = cls.get_parameter_from_dict(
                placeholder, parameter_dict)
            text = text.replace(placeholder.key, replacement)
        return text

    @classmethod
    def get_parameter_from_dict(cls, placeholder: Placeholder,
                                parameter_dict: dict) -> Any:

        parameter = parameter_dict.get(placeholder.name, None)

        if not parameter:
            return cls.PLACEHOLDER_NONE
        if cls.is_unquoted_param(placeholder, parameter):
            return str(parameter)
        else:
            return "'{}'".format(parameter)

    @classmethod
    def is_unquoted_param(cls, placeholder: Placeholder, parameter: Any):
        return placeholder.is_unquoted() \
               or not isinstance(parameter, str)
