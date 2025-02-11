import ast
import io
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
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


def _extract_parameters(node: ast.Call) -> Tuple[Any, Any, Any, Any]:
    kwargs: Dict[str, Any] = {}
    params = ["code", "message", "mitigations", "parameters"]

    for arg in node.args:
        name = params.pop(0)
        kwargs[name] = arg

    for keyword_argument in node.keywords:
        if current_arg := keyword_argument.arg:
            kwargs[current_arg] = keyword_argument.value

    return (
        kwargs["code"],
        kwargs["message"],
        kwargs["mitigations"],
        kwargs["parameters"],
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

    def validate(
        self, node: ast.Call, file: str
    ) -> Tuple[List["Validator.Error"], List["Validator.Warning"]]:
        code: ast.Constant
        message: ast.Constant
        mitigations: Union[ast.Constant, ast.List]
        parameters: ast.Dict

        code, message, mitigations, parameters = _extract_parameters(node)

        # TODO: Add/Collect additional warnings:
        #        * error message/mitigation defines a placeholder, but no parameter is provided
        #        * error defines a parameter, but it is never used
        # TODO: Add/Collect additional errors:
        #        * check for invalid error code format
        #
        # See also [Github Issue #23](https://github.com/exasol/error-reporting-python/issues/23)

        # make sure all parameters have the valid type
        self._validate_code(code, file)
        self._validate_message(message, file)
        self._validate_mitigations(mitigations, file)
        self._validate_parameters(parameters, file)

        return self._errors, self._warnings

    def _validate_code(self, code: ast.Constant, file: str) -> None:
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

    def _validate_message(self, node: ast.Constant, file: str) -> None:
        if not isinstance(node, ast.Constant):
            self._errors.append(
                self.Error(
                    message=self._error_msg.format(type="message", value=type(node)),
                    file=file,
                    line_number=node.lineno,
                )
            )

    def _validate_mitigations(
        self, node: Union[ast.Constant, ast.List], file: str
    ) -> None:
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

    def _validate_parameters(self, node: ast.Dict, file: str) -> None:
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

    def _make_error(self, node: ast.Call) -> ErrorCodeDetails:
        code: ast.Constant
        message: ast.Constant
        mitigations: Union[ast.List, ast.Constant]
        parameters: ast.Dict
        code, message, mitigations, parameters = _extract_parameters(node)

        def normalize(params):
            for k, v in zip(params.keys, params.keys):
                if isinstance(v, ast.Call):
                    yield k.value, v[1]
                else:
                    yield k.value, ""

        return ErrorCodeDetails(
            identifier=code.value,
            message=message.value,
            messagePlaceholders=[
                Placeholder(name, description)
                for name, description in normalize(parameters)
            ],
            description=None,
            internalDescription=None,
            potentialCauses=None,
            mitigations=(
                (
                    [m.value for m in mitigations.elts]  # type: ignore
                    if isinstance(mitigations, ast.List)
                    else [mitigations.value]
                )
                if not isinstance(mitigations, str)
                else [mitigations]
            ),
            sourceFile=self._filename,
            sourceLine=node.lineno,
            contextHash=None,
        )

    def collect(self) -> None:
        for node in _ExaErrorNodeWalker(self._root):
            errors, warnings = self._validator.validate(node, self._filename)
            if errors:
                # stop if we encountered any error
                return
            error_definition = self._make_error(node)
            self._error_definitions.append(error_definition)


def parse_file(file: Union[str, Path, io.FileIO]) -> Tuple[
    Iterable[ErrorCodeDetails],
    Iterable["Validator.Warning"],
    Iterable["Validator.Error"],
]:
    with ExitStack() as stack:
        f = file if isinstance(file, io.TextIOBase) else stack.enter_context(open(file))  # type: ignore
        root_node = ast.parse(f.read())
        name = f.name if hasattr(f, "name") else f"<{f.__class__.__name__}>"
        collector = ErrorCollector(root_node, name)
        collector.collect()

        return collector.error_definitions, collector.warnings, collector.errors
