from typing import Any

from exasol_error_reporting_python.placeholder_handler import PlaceholderHandler


class ParametersMapper:
    """
    This class is responsible for mapping positional arguments to corresponding
    placeholders in messages.
    """

    def __init__(self, text: str, arguments: str):
        self._text = text
        self._parameters = arguments
        self._parameter_idx = 0
        self._parameter_dict = {}

    @classmethod
    def get_params_dict(cls, text, arguments) -> dict:
        """
        Create ParametersMapper object and return the generated dictionary
        that maps the placeholders and parameters.

        :param text: message or mitigation that may contain placeholders
        :param arguments: arguments to replace with  the placeholders

        :return: a dictionary that maps the placeholders and parameters
        """

        parameters_mapper = cls(text, arguments)
        parameters_mapper._map_parameters()
        return parameters_mapper._parameter_dict

    def _map_parameters(self):
        """
        Parse the given text containing placeholders, look up the positional
        parameters and set the correct parameter mapping.
        """

        for placeholder in PlaceholderHandler.get_placeholders(self._text):
            if self._is_parameter_present():
                self._parameter_dict[placeholder.name] = self._get_current_parameter()
            self._next_parameters()

    def _get_current_parameter(self) -> Any:
        """
        Return the current parameter, if any.

        :return: a parameter in the parameters list or None
        """
        return (
            self._parameters[self._parameter_idx]
            if self._is_parameter_present()
            else None
        )

    def _is_parameter_present(self) -> bool:
        """
        Check whether the current parameter present.

        :return: True if present, False otherwise
        """
        return self._parameters and self._parameter_idx < len(self._parameters)

    def _next_parameters(self):
        """
        Increase index for parameter list.
        """

        self._parameter_idx += 1
