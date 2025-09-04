import ast
import sys
from inspect import cleandoc

import pytest

from exasol.error._error import Error
from exasol.error._internal_errors import INVALID_ERROR_CODE_DEFINITION
from exasol.error._parse import (
    ErrorCodeDetails,
    ErrorCollector,
    Placeholder,
    Validator,
)

AST_NAME_CLASS = "ast.Name" if sys.version_info.minor > 8 else "_ast.Name"


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
    collector = ErrorCollector(root_node)
    collector.collect()
    assert expected == collector.error_definitions


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
            [
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": "description",
                        "file": "<Unknown>",
                        "line": "10",
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
        ),
        (
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
                        "error_element": "error-codes",
                        "file": "<Unknown>",
                        "line": "7",
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
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
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
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
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
        ),
        (
            cleandoc(
                """
                                from exasol import error
                                from exasol.error import Parameter

                                var = input("description: ")

                                error1 = error.ExaError(
                                    "E-TEST-1",
                                    var,
                                    ["mitigations"],
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
                        "error_element": "message",
                        "file": "<Unknown>",
                        "line": "8",
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
        ),
        (
            cleandoc(
                """
                                from exasol import error
                                from exasol.error import Parameter

                                var = input("description: ")

                                error1 = error.ExaError(
                                    "E-TEST-1",
                                    var,
                                    ["mitigations"],
                                    {"param": Parameter("value", "")},
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
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
        ),
        (
            cleandoc(
                """
                                from exasol import error
                                from exasol.error import Parameter

                                var = input("description: ")

                                error1 = error.ExaError(
                                    "E-TEST-1",
                                    var,
                                    ["mitigations"],
                                    {"param": Parameter("value", None)},
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
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
        ),
(
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
                        "defined_type": f"<class '{AST_NAME_CLASS}'>",
                    },
                )
            ],
        ),
    ],
)
def test_ErrorCollector_errors(src, expected):
    root_node = ast.parse(src)
    collector = ErrorCollector(root_node)
    collector.collect()
    errors = list(collector.errors)
    assert len(expected) == len(errors)

    for idx_error in range(len(errors)):
        first_expected = expected[idx_error]
        first_error = errors[idx_error]

        assert first_error._error._error_code == first_expected._error._error_code
        assert (
            first_error._error._message_builder
            == first_expected._error._message_builder
        )
        assert first_error._error._mitigations == first_expected._error._mitigations
        assert (
            first_error._error._parameter_dict == first_expected._error._parameter_dict
        )


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
    collector = ErrorCollector(root_node)
    collector.collect()
    assert expected == collector.warnings
