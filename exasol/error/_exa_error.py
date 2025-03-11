from exasol.error._error_message_builder import ErrorMessageBuilder


class ExaError:
    """
    This class is only responsible for invoking ErrorMessageBuilder class.
    The structure of error-code is as follows:
        severity "-" project-short-tag ["-" module-short-tag] "-" error-number
        where,
            - severity: either F (Failure, not recoverable), or
            E (Error, recoverable), or W (warning),
            - project-short-tag: alphanumeric starting with alphabet.
            - module-short-tag: alphanumeric starting with alphabet.
            - error-number: only number.
    """

    @staticmethod
    def message_builder(error_code: str) -> ErrorMessageBuilder:
        """
        Create and return ErrorMessageBuilder object with the given error code.

        :param error_code:  a string error code

        :return: ErrorMessageBuilder object with the given error code
        """
        return ErrorMessageBuilder(error_code)
