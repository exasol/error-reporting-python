from exasol_error_reporting_python.placeholder_handler import PlaceholderHandler


class ParametersMapper:
    def __init__(self, text: str, arguments: str):
        self._text = text
        self._parameters = arguments
        self._parameter_idx = 0
        self._parameter_dict = {}

    @classmethod
    def get_params_dict(cls, text, arguments):
        parameters_mapper = cls(text, arguments)
        parameters_mapper._map_parameters()
        return parameters_mapper._parameter_dict

    def _map_parameters(self):
        for placeholder in PlaceholderHandler.get_placeholders(self._text):
            if self._is_parameter_present():
                self._parameter_dict[placeholder.name] = \
                    self._get_current_parameter()
            self._next_parameters()

    def _get_current_parameter(self):
        return self._parameters[self._parameter_idx] \
            if self._is_parameter_present() else None

    def _is_parameter_present(self):
        return self._parameters and \
               self._parameter_idx < len(self._parameters)

    def _next_parameters(self):
        self._parameter_idx += 1


