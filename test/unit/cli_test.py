"""
Unit tests for parsing error definitions in python files via Abstract
Syntax Tree (ast).
"""

import ast
import sys
from dataclasses import dataclass
from inspect import cleandoc

import pytest

from exasol.error._error import Error
from exasol.error._internal_errors import INVALID_ERROR_CODE_DEFINITION
from exasol.error._parse import (
    ErrorCodeDetails,
    ErrorCollector,
    Placeholder,
)

AST_NAME_CLASS = "ast.Name" if sys.version_info.minor > 8 else "_ast.Name"
AST_CONSTANT_CLASS = "ast.Constant" if sys.version_info.minor > 8 else "_ast.Constant"


@pytest.mark.parametrize(
    ["src", "expected"],
    [
        (
            cleandoc(
                """
                from exasol import error

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": error.Parameter("value", "description")},
                )
                """
            ),
            [
                ErrorCodeDetails(
                    identifier="E-TEST-1",
                    message="this is an error",
                    messagePlaceholders=[
                        Placeholder(placeholder="param", description="description")
                    ],
                    description=None,
                    internalDescription=None,
                    potentialCauses=None,
                    mitigations=["no mitigation available"],
                    sourceFile="<Unknown>",
                    sourceLine=3,
                    contextHash=None,
                )
            ],
        ),
        (
            cleandoc(
                """
                from exasol import error

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": error.Parameter("value", "")},
                )
                """
            ),
            [
                ErrorCodeDetails(
                    identifier="E-TEST-1",
                    message="this is an error",
                    messagePlaceholders=[
                        Placeholder(placeholder="param", description="")
                    ],
                    description=None,
                    internalDescription=None,
                    potentialCauses=None,
                    mitigations=["no mitigation available"],
                    sourceFile="<Unknown>",
                    sourceLine=3,
                    contextHash=None,
                )
            ],
        ),
        (
            cleandoc(
                """
                from exasol import error

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": error.Parameter("value", None)},
                )
                """
            ),
            [
                ErrorCodeDetails(
                    identifier="E-TEST-1",
                    message="this is an error",
                    messagePlaceholders=[
                        Placeholder(placeholder="param", description="")
                    ],
                    description=None,
                    internalDescription=None,
                    potentialCauses=None,
                    mitigations=["no mitigation available"],
                    sourceFile="<Unknown>",
                    sourceLine=3,
                    contextHash=None,
                )
            ],
        ),
        (
            cleandoc(
                """
                from exasol import error

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": error.Parameter("value")},
                )
                """
            ),
            [
                ErrorCodeDetails(
                    identifier="E-TEST-1",
                    message="this is an error",
                    messagePlaceholders=[
                        Placeholder(placeholder="param", description="")
                    ],
                    description=None,
                    internalDescription=None,
                    potentialCauses=None,
                    mitigations=["no mitigation available"],
                    sourceFile="<Unknown>",
                    sourceLine=3,
                    contextHash=None,
                )
            ],
        ),
    ],
)
def test_ErrorCollector_error_definitions(src, expected):
    root_node = ast.parse(src)
    collector = ErrorCollector(root_node).collect()
    assert expected == collector.error_definitions


@pytest.mark.parametrize(
    ["src", "expected"],
    [
        pytest.param(
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value", var)},
                )
                """
            ),
            [
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": "description",
                        "file": "<Unknown>",
                        "line": "10",
                        "defined_type": AST_NAME_CLASS,
                        "value_type": "(n/a)",
                    },
                )
            ],
            id="parameter",
        ),
        pytest.param(
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    var,
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value", "description")},
                )
                """
            ),
            [
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": "code",
                        "file": "<Unknown>",
                        "line": "7",
                        "defined_type": AST_NAME_CLASS,
                        "value_type": "(n/a)",
                    },
                )
            ],
            id="error_code",
        ),
        pytest.param(
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    [var],
                    {"param": Parameter("value", "description")},
                )
                """
            ),
            [
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": "mitigations",
                        "file": "<Unknown>",
                        "line": "9",
                        "defined_type": AST_NAME_CLASS,
                        "value_type": "(n/a)",
                    },
                )
            ],
            id="mitigation_list",
        ),
        pytest.param(
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    var,
                    {"param": Parameter("value", "description")},
                )
                """
            ),
            [
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": "mitigations",
                        "file": "<Unknown>",
                        "line": "9",
                        "defined_type": AST_NAME_CLASS,
                        "value_type": "(n/a)",
                    },
                )
            ],
            id="mitigation",
        ),
        pytest.param(
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    var,
                    ["mitigations"],
                    {"param": Parameter("value")},
                )
                """
            ),
            [
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": "message",
                        "file": "<Unknown>",
                        "line": "8",
                        "defined_type": AST_NAME_CLASS,
                        "value_type": "(n/a)",
                    },
                )
            ],
            id="message",
        ),
    ],
)
def test_error_definition_not_constant(src, expected):
    """
    Error definitions in Python files may only use constant values. This
    test verifies parsing errors for non-constant values being used as error
    code, description, or in the list of parameters.
    """
    node = ast.parse(src)
    collector = ErrorCollector(node).collect()
    actual = list(collector.errors)
    assert actual == expected


@dataclass(frozen=True)
class ExpectedError:
    element: str
    type_name: str


def expected_error(element_name: str, type_name: str):
    return ExpectedError(element_name, type_name)


@pytest.mark.parametrize(
    ["src", "expected"],
    [
        (
            'ExaError(123, "message", ["mitigation"], {})',
            expected_error("code", "int"),
        ),
        (
            'ExaError("E-TEST-1", True, ["mitigation"], {})',
            expected_error("message", "bool"),
        ),
        (
            'ExaError("E-TEST-1", "descriptive text", 0.5, {})',
            expected_error("mitigations", "float"),
        ),
        (
            'ExaError("E-TEST-1", "message", ["mitigation"], {123: Parameter("value")})',
            expected_error("parameter keys", "int"),
        ),
    ],
)
def test_value_not_string(src, expected) -> None:
    """
    Verify parsing errors in case a non-string value is provided for an
    error attribute such as code, message or mitigation.
    """
    expected_error = Error(
        code=INVALID_ERROR_CODE_DEFINITION.identifier,
        message=INVALID_ERROR_CODE_DEFINITION.message,
        mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
        parameters={
            "error_element": expected.element,
            "file": "<Unknown>",
            "line": "3",
            "defined_type": AST_CONSTANT_CLASS,
            "value_type": expected.type_name,
        },
    )
    node = ast.parse("from exasol.error import ExaError, Parameter\n\n" + src)
    collector = ErrorCollector(node).collect()
    actual = list(collector.errors)
    assert actual == [expected_error]


@pytest.mark.parametrize(
    ["src", "expected"],
    [
        (
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value", var)},
                )
                """
            ),
            [],
        ),
        (
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value", "description")},
                )
                """
            ),
            [],
        ),
        (
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value", "")},
                )
                """
            ),
            [],
        ),
        (
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value", None)},
                )
                """
            ),
            [],
        ),
        (
            cleandoc(
                """
                from exasol import error
                from exasol.error import Parameter

                var = input("description: ")

                error1 = error.ExaError(
                    "E-TEST-1",
                    "this is an error",
                    ["no mitigation available"],
                    {"param": Parameter("value")},
                )
                """
            ),
            [],
        ),
    ],
)
def test_ErrorCollector_warnings(src, expected):
    root_node = ast.parse(src)
    collector = ErrorCollector(root_node).collect()
    assert expected == collector.warnings
