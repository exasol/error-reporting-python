from exasol_error_reporting_python.error_message_builder import \
    ErrorMessageBuilder


def test_message():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1").
                  message("Test message"))
    assert message == "E-ERJ-TEST-1: Test message"


def test_mitigation():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1").
                  message("Something went wrong.").
                  mitigation("Fix it."))
    assert message == "E-ERJ-TEST-1: Something went wrong. Fix it."


def test_mitigations():
    support_hotline = "1234/56789"
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1").
                  message("Something went wrong.").
                  mitigation("Fix it.").
                  mitigation(f"Contact support under '{support_hotline}'."))
    assert message == "E-ERJ-TEST-1: Something went wrong. Known mitigations:" \
                      "\n* Fix it.\n* Contact support under '1234/56789'."


def test_ticket_mitigation():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1").
                  message("Something went wrong.").
                  ticket_mitigation())
    assert message == "E-ERJ-TEST-1: Something went wrong. " \
                      "This is an internal error that should not happen. " \
                      "Please report it by opening a GitHub issue."
