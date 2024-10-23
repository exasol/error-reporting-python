import io
from inspect import cleandoc

import pytest

from exasol.error._parse import parse_file
from exasol.error._report import ErrorCodeDetails


@pytest.fixture
def expected():
    yield (
        [
            ErrorCodeDetails(
                identifier="E-TEST-1",
                message="this is an error",
                messagePlaceholders=[],
                description=None,
                internalDescription=None,
                potentialCauses=None,
                mitigations=["no mitigation available"],
                sourceFile="<StringIO>",
                sourceLine=6,
                contextHash=None,
            ),
        ],
        [],
        [],
    )


def test_use_only_named_parameters(expected):
    file = io.StringIO(
        initial_value=cleandoc(
            """
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")

        error1 = error.ExaError(
            code="E-TEST-1",
            message="this is an error",
            mitigations="no mitigation available",
            parameters={},
        )
        """
        )
    )

    expected_defs, expected_warnings, expected_errors = expected
    definitions, warnings, errors = parse_file(file)

    assert expected_defs == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors


def test_dont_name_the_code_parameter(expected):
    file = io.StringIO(
        initial_value=cleandoc(
            """
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")

        error1 = error.ExaError(
            "E-TEST-1",
            message="this is an error",
            mitigations="no mitigation available",
            parameters={},
        )
        """
        )
    )

    expected_defs, expected_warnings, expected_errors = expected
    definitions, warnings, errors = parse_file(file)

    assert expected_defs == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors


def test_dont_name_the_code_and_message_parameter(expected):
    file = io.StringIO(
        initial_value=cleandoc(
            """
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")

        error1 = error.ExaError(
            "E-TEST-1",
            "this is an error",
            mitigations="no mitigation available",
            parameters={},
        )
        """
        )
    )

    expected_defs, expected_warnings, expected_errors = expected
    definitions, warnings, errors = parse_file(file)

    assert expected_defs == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors


def test_dont_name_the_code_message_and_mitigations_parameter(expected):
    file = io.StringIO(
        initial_value=cleandoc(
            """
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")

        error1 = error.ExaError(
            "E-TEST-1",
            "this is an error",
            "no mitigation available",
            parameters={},
        )
        """
        )
    )

    expected_defs, expected_warnings, expected_errors = expected
    definitions, warnings, errors = parse_file(file)

    assert expected_defs == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors


def test_dont_name_any_parameter(expected):
    file = io.StringIO(
        initial_value=cleandoc(
            """
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")

        error1 = error.ExaError(
            "E-TEST-1",
            "this is an error",
            "no mitigation available",
            {},
        )
        """
        )
    )

    expected_defs, expected_warnings, expected_errors = expected
    definitions, warnings, errors = parse_file(file)

    assert expected_defs == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors
