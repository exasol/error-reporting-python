from exasol_error_reporting_python.exa_error import ExaError


def test_message_builder():
    assert str(ExaError.message_builder("E-ERJ-TEST-1")) == "E-ERJ-TEST-1"
