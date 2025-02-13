import ast
import io
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
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
    kwargs: Dict[str, ast.expr] = {}
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
    class Error:
        message: str
        file: str
        line_number: Optional[int]

    @dataclass(frozen=True)
    class Warning:
        message: str
        file: str
        line_number: Optional[int]

    @dataclass(frozen=True)
    class ExaValidatedNode:
        code: str
        message: str
        mitigations: List[str]
        parameters: List[Tuple[str, str]]
        lineno: int

    @dataclass(frozen=True)
    class Result:
        errors: List["Validator.Error"]
        warnings: List["Validator.Warning"]
        node: Optional["Validator.ExaValidatedNode"]

    def __init__(self) -> None:
        self._warnings: List["Validator.Warning"] = list()
        self._errors: List[Validator.Error] = list()
        self._error_msg = "{type} only can contain constant values, details: {value}"

    @property
    def errors(self) -> Iterable["Validator.Error"]:
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

    def _validate_code(self, code: ast.expr, file: str) -> Optional[str]:
        if not isinstance(code, ast.Constant):
            self._errors.append(
                self.Error(
                    message=self._error_msg.format(
                        type="error-codes", value=type(code)
                    ),
                    file=file,
                    line_number=code.lineno,
                )
            )
            return None
        else:
            return code.value

    def _validate_message(self, node: ast.expr, file: str) -> Optional[str]:
        if not isinstance(node, ast.Constant):
            self._errors.append(
                self.Error(
                    message=self._error_msg.format(type="message", value=type(node)),
                    file=file,
                    line_number=node.lineno,
                )
            )
            return None
        else:
            return node.value

    def _validate_mitigations(self, node: ast.expr, file: str) -> Optional[List[str]]:
        if not isinstance(node, ast.List) and not isinstance(node, ast.Constant):
            self._errors.append(
                self.Error(
                    message=self._error_msg.format(
                        type="mitigations", value=type(node)
                    ),
                    file=file,
                    line_number=node.lineno,
                )
            )
            return None
        if isinstance(node, ast.List):
            invalid = [e for e in node.elts if not isinstance(e, ast.Constant)]
            self._errors.extend(
                [
                    self.Error(
                        message=self._error_msg.format(
                            type="mitigations", value=type(e)
                        ),
                        file=file,
                        line_number=e.lineno,
                    )
                    for e in invalid
                ]
            )
            if invalid:
                return None
            else:
                return [e.value for e in node.elts if isinstance(e, ast.Constant)]
        elif isinstance(node, ast.Constant):
            return [node.value]
        return None

    def _validate_parameters(
        self, node: ast.expr, file: str
    ) -> Optional[List[Tuple[str, str]]]:
        def normalize(params):
            for k, v in zip(params.keys, params.keys):
                if isinstance(v, ast.Call):
                    yield k.value, v[1]
                else:
                    yield k.value, ""

        if not isinstance(node, ast.Dict):
            self._errors.append(
                self.Error(
                    message=self._error_msg.format(type="parameters", value=type(node)),
                    file=file,
                    line_number=node.lineno,
                )
            )
            return None
        else:
            is_ok = True
            # Validate parameters
            for key in node.keys:
                if not isinstance(key, ast.Constant) and key is not None:
                    self._errors.append(
                        self.Error(
                            message=self._error_msg.format(type="key", value=type(key)),
                            file=file,
                            line_number=key.lineno,
                        )
                    )
                    is_ok = False
            for value in node.values:
                if isinstance(value, ast.Call):
                    description = value.args[1]
                    if not isinstance(description, ast.Constant):
                        self._errors.append(
                            self.Error(
                                message=self._error_msg.format(
                                    type="description", value=type(description)
                                ),
                                file=file,
                                line_number=value.lineno,
                            )
                        )
                        is_ok = False
            if is_ok:
                return list(normalize(node))
            else:
                return None


class ErrorCollector:
    def __init__(self, root: ast.AST, filename: str = "<Unknown>") -> None:
        self._filename = filename
        self._root = root
        self._validator = Validator()
        self._error_definitions: List[ErrorCodeDetails] = list()

    @property
    def error_definitions(self) -> List[ErrorCodeDetails]:
        return self._error_definitions

    @property
    def errors(self) -> Iterable["Validator.Error"]:
        return self._validator.errors

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
                raise Exception(
                    "Validation finished with invalid result, but no error was set"
                )
            error_definition = self._make_error(validatation_result.node)
            self._error_definitions.append(error_definition)


def parse_file(file: Union[str, Path, io.TextIOBase]) -> Tuple[
    Iterable[ErrorCodeDetails],
    Iterable["Validator.Warning"],
    Iterable["Validator.Error"],
]:
    with ExitStack() as stack:
        f = file if isinstance(file, io.TextIOBase) else stack.enter_context(open(file))
        root_node = ast.parse(f.read())
        name = f.name if hasattr(f, "name") else f"<{f.__class__.__name__}>"
        collector = ErrorCollector(root_node, name)
        collector.collect()

        return collector.error_definitions, collector.warnings, collector.errors
