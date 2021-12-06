import unittest
from exasol_error_reporting_python.error_message_builder import \
    ErrorMessageBuilder


def test_message():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Test message"))
    assert message == "E-ERJ-TEST-1: Test message"


def test_message_with_parameter():
    message = str(ErrorMessageBuilder('E-ERJ-TEST-1')
                  .message("Test message {{my_placeholder}} " 
                           "and a number {{number}}.")
                  .parameter("my_placeholder", "my_value")
                  .parameter("number", 1, "a number"))
    assert message == "E-ERJ-TEST-1: Test message 'my_value' and a number 1."


def test_message_with_none_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("{{my_placeholder}}")
                  .parameter("my_placeholder", None))
    assert message == "E-ERJ-TEST-1: <null>"


def test_message_without_parameter_name():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("test {{}}"))  # TODO: different imp.
    assert message == "E-ERJ-TEST-1: test <null>"


def test_message_without_parameter_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("test {{my_placeholder}}"))  # TODO: different imp.
    assert message == "E-ERJ-TEST-1: test <null>"


def test_message_with_group_reference_char():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("test {{my_placeholder}}")
                  .parameter("my_placeholder", "$2"))
    assert message == "E-ERJ-TEST-1: test '$2'"


def test_single_mitigation():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Fix it."))
    assert message == "E-ERJ-TEST-1: Something went wrong. Fix it."


def test_single_mitigation_with_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Delete line {{LINE_NR}}.")
                  .parameter("LINE_NR", 1))
    assert message == "E-ERJ-TEST-1: Something went wrong. Delete line 1."


def test_mitigations():
    support_hotline = "1234/56789"
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Fix it.")
                  .mitigation("Contact support under {{SUPPORT_HOTLINE}}.")
                  .parameter("SUPPORT_HOTLINE", support_hotline))
    assert message == "E-ERJ-TEST-1: Something went wrong. Known mitigations:" \
                      "\n* Fix it.\n* Contact support under '1234/56789'."


def test_ticket_mitigation():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .ticket_mitigation())
    assert message == "E-ERJ-TEST-1: Something went wrong. " \
                      "This is an internal error that should not happen. " \
                      "Please report it by opening a GitHub issue."


def test_mitigation_inline_single_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Delete line {{LINE_NR}}.", 1))
    assert message == "E-ERJ-TEST-1: Something went wrong. Delete line 1."


def test_mitigation_inline_multiple_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Delete lines {{LINE_NR1}}, {{LINE_NR2}}", 1, 2))
    assert message == "E-ERJ-TEST-1: Something went wrong. Delete lines 1, 2"


def test_mitigation_inline_parameter_without_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Delete line {{LINE_NR}}."))  # TODO: different imp.
    assert message == "E-ERJ-TEST-1: Something went wrong. Delete line <null>."


def test_mitigation_inline_single_null_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Delete line {{LINE_NR}}.", None))
    assert message == "E-ERJ-TEST-1: Something went wrong. Delete line <null>."


def test_mitigation_inline_multiple_null_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Something went wrong.")
                  .mitigation("Delete lines {{LINE1}}, {{LINE2}}.", None, None))
    assert message == "E-ERJ-TEST-1: Something went wrong. " \
                      "Delete lines <null>, <null>."


def test_message_inline_single_unquoted_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name|uq}}.", "value"))
    assert message == "E-ERJ-TEST-1: Message with value."


def test_message_inline_single_quoted_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name}}.", "value"))
    assert message == "E-ERJ-TEST-1: Message with 'value'."


def test_message_inline_multiple_unquoted_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name1|uq}} and "
                           "{{parameter_name2|uq}}.", "value1", "value2"))
    assert message == "E-ERJ-TEST-1: Message with value1 and value2."


def test_message_inline_multiple_quoted_parameter():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name1}} and "
                           "{{parameter_name2}}.", "value1", "value2"))
    assert message == "E-ERJ-TEST-1: Message with 'value1' and 'value2'."


def test_message_inline_unquoted_parameter_without_name():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{|uq}}.", "value"))
    assert message == "E-ERJ-TEST-1: Message with value."


def test_message_inline_unquoted_parameter_without_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name|uq}}."))
    assert message == "E-ERJ-TEST-1: Message with <null>."


def test_message_inline_single_unquoted_parameter_none_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name|uq}}.", None))
    assert message == "E-ERJ-TEST-1: Message with <null>."


def test_message_inline_multiple_unquoted_parameter_none_value():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name|uq}} and "
                           "{{parameter_name2}}.", None, None))
    assert message == "E-ERJ-TEST-1: Message with <null> and <null>."


def test_message_inline_multiple_unquoted_parameter_none_parameters():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name|uq}} and "
                           "{{parameter_name2}}.")
                  .parameter("parameter_name", None)
                  .parameter("parameter_name2", None))
    assert message == "E-ERJ-TEST-1: Message with <null> and <null>."


def test_message_inline_unquoted_parameter_with_group_reference_char():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("test {{my_placeholder|uq}}")
                  .parameter("my_placeholder", "$2"))
    assert message == "E-ERJ-TEST-1: test $2"


def test_message_inline_and_outline_order():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name1}}", "value1")
                  .message(" {{parameter_name2}}.", "value2"))
    assert message == "E-ERJ-TEST-1: Message with 'value1' 'value2'."


def test_message_inline_and_outline_unquoted_parameters():
    message = str(ErrorMessageBuilder("E-ERJ-TEST-1")
                  .message("Message with {{parameter_name1|uq}}", "value1")
                  .message(" {{parameter_name2|uq}}.", "value2"))
    assert message == "E-ERJ-TEST-1: Message with value1 value2."


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
