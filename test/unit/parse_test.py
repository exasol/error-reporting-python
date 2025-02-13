import io
from inspect import cleandoc

import pytest

from exasol.error._parse import (
    Validator,
    parse_file,
)
from exasol.error._report import ErrorCodeDetails


@pytest.mark.parametrize(
    "mitigation_str, mitigation",
    [
        ("'str mitigation'", ["str mitigation"]),
        ("42", [42]),
        ("""['mitigation a', 42.5]""", ["mitigation a", 42.5]),
    ],
)
def test_mitigation_values(mitigation_str, mitigation):
    f = io.StringIO(
        initial_value=cleandoc(
            f"""
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")

        error1 = error.ExaError(
            "E-TEST-1",
            "this is an error",
            {mitigation_str},
            {{}},
        )
        """
        )
    )

    expected_definitions = [
        ErrorCodeDetails(
            identifier="E-TEST-1",
            message="this is an error",
            messagePlaceholders=[],
            description=None,
            internalDescription=None,
            potentialCauses=None,
            mitigations=mitigation,
            sourceFile="<StringIO>",
            sourceLine=6,
            contextHash=None,
        ),
    ]
    expected_warnings = []
    expected_errors = []

    definitions, warnings, errors = parse_file(f)

    assert expected_definitions == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors


def test_mitigation_none_constant_fails():
    f = io.StringIO(
        initial_value=cleandoc(
            f"""
        from exasol import error
        from exasol.error import Parameter

        var = input("description: ")
        a = 42
        b = 100
        error1 = error.ExaError(
            "E-TEST-1",
            "this is an error",
            a + b,
            {{}},
        )
        """
        )
    )

    expected_definitions = []
    expected_warnings = []
    expected_errors = [
        Validator.Error(
            message="mitigations only can contain constant values, details: <class 'ast.BinOp'>",
            file="<StringIO>",
            line_number=10,
        )
    ]

    definitions, warnings, errors = parse_file(f)

    assert expected_definitions == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors
