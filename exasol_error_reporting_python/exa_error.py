from exasol_error_reporting_python.error_message_builder import \
    ErrorMessageBuilder


class ExaError:
    @staticmethod
    def message_builder(error_code: str):
        return ErrorMessageBuilder(error_code)
