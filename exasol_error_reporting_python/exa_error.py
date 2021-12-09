from exasol_error_reporting_python.error_message_builder import \
    ErrorMessageBuilder


class ExaError:
    """
    This class is only responsible for invoking ErrorMessageBuilder class.
    """

    @staticmethod
    def message_builder(error_code: str) -> ErrorMessageBuilder:
        """
        Create and return ErrorMessageBuilder object with the given error code.

        :param error_code:  a string error code

        :return: ErrorMessageBuilder object with the given error code
        """
        return ErrorMessageBuilder(error_code)
