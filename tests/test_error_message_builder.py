import unittest

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


class TestErrorCode(unittest.TestCase):
    def test_invalid_error_code_format(self):
        invalid_error_code_list = [
            "A-EXA-100",
            "F1-EXA-100",
            "F-1EXA-100",
            "F-EXA-EXA-F1"
            "F-EXA-EXA",
            "F-100"
        ]
        for error_code in invalid_error_code_list:
            with self.assertRaises(AssertionError):
                builder = ErrorMessageBuilder(error_code)

    def test_valid_error_code_format(self):
        valid_error_code_list = [
            "F-EXA-100",
            "E-EXA-EXA-100",
            "W-E6-EXA-1001"
        ]
        for error_code in valid_error_code_list:
            self.assertTrue(ErrorMessageBuilder(error_code))
