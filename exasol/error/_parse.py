import ast
import io
from collections.abc import (
    Generator,
    Iterable,
    Iterator,
)
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from exasol.error._error import Error
from exasol.error._internal_errors import (
    INTERNAL_ERROR_WHEN_CREATING_ERROR_CATALOG,
    INVALID_ERROR_CODE_DEFINITION,
)
from exasol.error._report import (
    ErrorCodeDetails,
    Placeholder,
)


@dataclass(frozen=True)
class _ExaErrorAttributes:
    code: ast.expr
    message: ast.expr
    mitigations: ast.expr
    parameters: ast.expr


class _ExaErrorNodeWalker:
    @staticmethod
    def _is_exa_error(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        name = getattr(node.func, "id", "")
        name = getattr(node.func, "attr", "") if name == "" else name
        return name == "ExaError"

    def __init__(self, root_node: ast.AST) -> None:
        self._root = root_node

    def __iter__(self) -> Generator[ast.Call, None, None]:
        return (
            node
            for node in ast.walk(self._root)
            if _ExaErrorNodeWalker._is_exa_error(node) and isinstance(node, ast.Call)
        )


def _extract_attributes(node: ast.Call) -> _ExaErrorAttributes:
    kwargs: dict[str, ast.expr] = {}
    params = ["code", "message", "mitigations", "parameters"]

    for arg in node.args:
        name = params.pop(0)
        kwargs[name] = arg

    for keyword_argument in node.keywords:
        if current_arg := keyword_argument.arg:
            kwargs[current_arg] = keyword_argument.value
    return _ExaErrorAttributes(
        code=kwargs["code"],
        message=kwargs["message"],
        mitigations=kwargs["mitigations"],
        parameters=kwargs["parameters"],
    )


class Validator:

    @dataclass(frozen=True)
    class Warning:
        message: str
        file: str
        line_number: Optional[int]

    @dataclass(frozen=True)
    class ExaValidatedNode:
        code: str
        message: str
        mitigations: list[str]
        parameters: list[tuple[str, str]]
        lineno: int

    @dataclass(frozen=True)
    class Result:
        errors: list[Error]
        warnings: list["Validator.Warning"]
        node: Optional["Validator.ExaValidatedNode"]

    def __init__(self) -> None:
        self._warnings: list["Validator.Warning"] = []
        self._errors: list[Error] = []

    @property
    def errors(self) -> Iterable[Error]:
        return self._errors

    @property
    def warnings(self) -> Iterable["Validator.Warning"]:
        return self._warnings

    def validate(self, node: ast.Call, file: str) -> Result:
        code: ast.Constant
        message: ast.Constant
        mitigations: Union[ast.Constant, ast.List]
        parameters: ast.Dict

        error_attributes = _extract_attributes(node)

        # TODO: Add/Collect additional warnings:
        #        * error message/mitigation defines a placeholder, but no parameter is provided
        #        * error defines a parameter, but it is never used
        # TODO: Add/Collect additional errors:
        #        * check for invalid error code format
        #
        # See also [Github Issue #23](https://github.com/exasol/error-reporting-python/issues/23)

        # make sure all parameters have the valid type
        code_validated = self._validate_code(error_attributes.code, file)
        message_validated = self._validate_message(error_attributes.message, file)
        mitigations_validated = self._validate_mitigations(
            error_attributes.mitigations, file
        )
        parameters_validated = self._validate_parameters(
            error_attributes.parameters, file
        )
        validated_node = None
        if (
            code_validated is not None
            and message_validated is not None
            and mitigations_validated is not None
            and parameters_validated is not None
        ):
            validated_node = Validator.ExaValidatedNode(
                code=code_validated,
                message=message_validated,
                mitigations=mitigations_validated,
                parameters=parameters_validated,
                lineno=node.lineno,
            )

        return Validator.Result(
            errors=self._errors,
            warnings=self._warnings,
            node=validated_node,
        )

    NodeType = TypeVar("NodeType", bound=ast.expr)

    def _check_node_type(
        self,
        expected_type: type[NodeType],
        node: ast.expr,
        error_attribute: str,
        file: str,
    ) -> Optional[NodeType]:
        """
        This function validates if the given AST node ('node')  matches type 'expected_type'.
        If it matches, then it returns it as type 'expected_type', otherwise it adds it to the internal
        error list and return None.
        """
        if not isinstance(node, expected_type):
            self._errors.append(
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": error_attribute,
                        "file": file,
                        "line": str(node.lineno),
                        "defined_type": str(type(node)),
                    },
                )
            )
            return None
        return node

    def _check_node_types(
        self,
        expected_type_one: type[NodeType],
        expected_type_two: type[NodeType],
        node: ast.expr,
        error_attribute: str,
        file: str,
    ) -> Optional[NodeType]:
        """
        This function validates if the given AST node ('node')  matches type 'expected_type_one' or 'expected_type_two'.
        If it matches, then it returns it as type `expected_type_one` or `expected_type_two`,
        otherwise it adds it to the internal error list and return None.
        """
        if not isinstance(node, (expected_type_one, expected_type_two)):
            self._errors.append(
                Error(
                    code=INVALID_ERROR_CODE_DEFINITION.identifier,
                    message=INVALID_ERROR_CODE_DEFINITION.message,
                    mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                    parameters={
                        "error_element": error_attribute,
                        "file": file,
                        "line": str(node.lineno),
                        "defined_type": str(type(node)),
                    },
                )
            )
            return None
        return node

    def _validate_code(self, node: ast.expr, file: str) -> Optional[str]:
        if code := self._check_node_type(ast.Constant, node, "error-codes", file):
            return code.value
        return None

    def _validate_message(self, node: ast.expr, file: str) -> Optional[str]:
        if message := self._check_node_type(ast.Constant, node, "message", file):
            return message.value
        return None

    def _validate_mitigations(self, node: ast.expr, file: str) -> Optional[list[str]]:
        if mitigation := self._check_node_types(
            ast.List, ast.Constant, node, "mitigations", file
        ):
            if isinstance(mitigation, ast.List):
                invalid = [
                    e for e in mitigation.elts if not isinstance(e, ast.Constant)
                ]
                self._errors.extend(
                    [
                        Error(
                            code=INVALID_ERROR_CODE_DEFINITION.identifier,
                            message=INVALID_ERROR_CODE_DEFINITION.message,
                            mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                            parameters={
                                "error_element": "mitigations",
                                "file": file,
                                "line": str(node.lineno),
                                "defined_type": str(type(e)),
                            },
                        )
                        for e in invalid
                    ]
                )
                if invalid:
                    return None
                else:
                    return [
                        e.value for e in mitigation.elts if isinstance(e, ast.Constant)
                    ]
            elif isinstance(mitigation, ast.Constant):
                return [mitigation.value]
        return None

    def normalize(self, params: ast.Dict) -> Iterator[tuple[str, str]]:
        for k, v in zip(params.keys, params.values):
            if (
                isinstance(v, ast.Call)
                and isinstance(k, ast.Constant)
                and k.value is not None
                and isinstance(v.args[1], ast.Constant)
                and v.args[1].value is not None
            ):
                yield k.value, v.args[1].value
            elif isinstance(k, ast.Constant) and k.value is not None:
                yield k.value, ""

    def _validate_parameter_keys(self, parameter_node: ast.Dict, file: str) -> bool:
        """
        Checks if keys of ast dictionary are of expected type.
        If the keys are of expected type, the method returns True, otherwise False.
        """
        ret_val = True
        for key in parameter_node.keys:
            # The type of ast.Dict.keys is List[Optional[ast.expr]], not List[ast.expr] as someone would expect.
            # However, trying unit tests with parameters of kind {None: "something"} did not provoke the "key" to be None.
            # Nevertheless, keep the following error handling, in case of some strange corner case resulting "key" to be None.
            if key is None:
                self._errors.append(
                    Error(
                        code=INVALID_ERROR_CODE_DEFINITION.identifier,
                        message=INVALID_ERROR_CODE_DEFINITION.message,
                        mitigations=INVALID_ERROR_CODE_DEFINITION.mitigations,
                        parameters={
                            "error_element": "parameter keys",
                            "file": file,
                            "line": str(parameter_node.lineno),
                            "defined_type": "NoneType",
                        },
                    )
                )
                ret_val = False
            elif not self._check_node_type(ast.Constant, key, "key", file):
                ret_val = False
        return ret_val

    def _validate_parameter_values(self, parameter_node: ast.Dict, file: str) -> bool:
        """
        Checks if value of ast dictionary are of expected type.
        If the values are of expected type, the method returns True, otherwise False.
        """
        ret_val = True
        for value in parameter_node.values:
            if isinstance(value, ast.Call):
                if len(value.args) < 2:
                    value.args.append(ast.Constant(value=None))
                description = value.args[1]
                if not self._check_node_type(
                    ast.Constant, description, "description", file
                ):
                    ret_val = False
        return ret_val

    def _validate_parameters(
        self, node: ast.expr, file: str
    ) -> Optional[list[tuple[str, str]]]:

        if parameters := self._check_node_type(ast.Dict, node, "parameters", file):
            is_ok = self._validate_parameter_keys(
                parameters, file
            ) and self._validate_parameter_values(parameters, file)
            if is_ok:
                return list(self.normalize(parameters))
            return None
        return None


class ErrorCollector:
    def __init__(self, root: ast.AST, filename: str = "<Unknown>") -> None:
        self._filename = filename
        self._root = root
        self._validator = Validator()
        self._errors: list[Error] = []
        self._error_definitions: list[ErrorCodeDetails] = []

    @property
    def error_definitions(self) -> list[ErrorCodeDetails]:
        return self._error_definitions

    @property
    def errors(self) -> Iterable[Error]:
        return list(self._validator.errors) + self._errors

    @property
    def warnings(self) -> Iterable["Validator.Warning"]:
        return self._validator.warnings

    def _make_error(
        self, validated_node: Validator.ExaValidatedNode
    ) -> ErrorCodeDetails:

        return ErrorCodeDetails(
            identifier=validated_node.code,
            message=validated_node.message,
            messagePlaceholders=[
                Placeholder(name, description)
                for name, description in validated_node.parameters
            ],
            description=None,
            internalDescription=None,
            potentialCauses=None,
            mitigations=validated_node.mitigations,
            sourceFile=self._filename,
            sourceLine=validated_node.lineno,
            contextHash=None,
        )

    def collect(self) -> None:
        for node in _ExaErrorNodeWalker(self._root):
            validatation_result = self._validator.validate(node, self._filename)
            if validatation_result.errors:
                # stop if we encountered any error
                return
            if validatation_result.node is None:
                import traceback

                stack_summary = traceback.extract_stack()
                formatted_traceback = "".join(traceback.format_list(stack_summary))
                self._errors.append(
                    Error(
                        code=INTERNAL_ERROR_WHEN_CREATING_ERROR_CATALOG.identifier,
                        message=INTERNAL_ERROR_WHEN_CREATING_ERROR_CATALOG.message,
                        mitigations=INTERNAL_ERROR_WHEN_CREATING_ERROR_CATALOG.mitigations,
                        parameters={"traceback": formatted_traceback},
                    )
                )
            else:
                error_definition = self._make_error(validatation_result.node)
                self._error_definitions.append(error_definition)


def parse_file(file: Union[str, Path, io.TextIOBase]) -> tuple[
    Iterable[ErrorCodeDetails],
    Iterable["Validator.Warning"],
    Iterable[Error],
]:
    with ExitStack() as stack:
        f = file if isinstance(file, io.TextIOBase) else stack.enter_context(open(file))
        root_node = ast.parse(f.read())
        name = f.name if hasattr(f, "name") else f"<{f.__class__.__name__}>"
        collector = ErrorCollector(root_node, name)
        collector.collect()

        return collector.error_definitions, collector.warnings, collector.errors
