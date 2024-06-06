import io
from inspect import cleandoc

from exasol.error._parse import parse_file
from exasol.error._report import ErrorCodeDetails


# regression test for GitHub Issue #26
def test_single_mitigation():
    f = io.StringIO(initial_value=cleandoc(
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
    ))

    expected_definitions = [
        ErrorCodeDetails(
            identifier='E-TEST-1',
            message='this is an error',
            messagePlaceholders=[],
            description=None,
            internalDescription=None,
            potentialCauses=None,
            mitigations=['no mitigation available'],
            sourceFile='<StringIO>',
            sourceLine=6,
            contextHash=None),
    ]
    expected_warnings = []
    expected_errors = []

    definitions, warnings, errors = parse_file(f)

    assert expected_definitions == definitions
    assert expected_warnings == warnings
    assert expected_errors == errors
