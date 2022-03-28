import unittest

import pytest

from exasol_error_reporting_python.error_message_builder import \
    ErrorMessageBuilder


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
            with pytest.raises(ValueError):
                assert ErrorMessageBuilder(error_code)

    def test_valid_error_code_format(self):
        valid_error_code_list = [
            "F-EXA-100",
            "E-EXA-EXA-100",
            "W-E6-EXA-1001"
        ]
        for error_code in valid_error_code_list:
            self.assertTrue(ErrorMessageBuilder(error_code))
