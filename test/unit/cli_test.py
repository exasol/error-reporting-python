import ast
from inspect import cleandoc

import pytest

from exasol.error._cli import ErrorCodeDetails, ErrorCollector, Placeholder, Validation


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
                Validation.Error(
                    message="description only can contain constant values, details: <class 'ast.Name'>",
                    file="<Unknown>",
                    line_number=10,
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
                Validation.Error(
                    message="error-codes only can contain constant values, details: <class 'ast.Name'>",
                    file="<Unknown>",
                    line_number=7,
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
                Validation.Error(
                    message="mitigations only can contain constant values, details: <class 'ast.Name'>",
                    file="<Unknown>",
                    line_number=9,
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
                Validation.Error(
                    message="mitigations only can contain constant values, details: <class 'ast.Name'>",
                    file="<Unknown>",
                    line_number=9,
                )
            ],
        ),
    ],
)
def test_ErrorCollector_errors(src, expected):
    root_node = ast.parse(src)
    collector = ErrorCollector(root_node)
    collector.collect()
    assert expected == collector.errors


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
    ],
)
def test_ErrorCollector_warnings(src, expected):
    root_node = ast.parse(src)
    collector = ErrorCollector(root_node)
    collector.collect()
    assert expected == collector.warnings
