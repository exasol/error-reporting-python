import warnings


class ErrorReportingDeprecationWarning(DeprecationWarning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    pass


warnings.warn(
    f"The package {__name__} is deprecated, please use the 'exasol.error' package instead.",
    ErrorReportingDeprecationWarning,
    stacklevel=2,
)

__version__ = "0.4.0"
