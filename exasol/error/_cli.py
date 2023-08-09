import argparse
import ast
import io
import json
import sys
from contextlib import ExitStack
from dataclasses import asdict, dataclass, is_dataclass
from enum import IntEnum
from itertools import chain
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Tuple, Union


class ExitCode(IntEnum):
    SUCCESS = 0
    FAILURE = -1


@dataclass(frozen=True)
class Placeholder:
    """
    Placeholder according to schema specification.
    https://schemas.exasol.com/error_code_report-1.0.0.json
    """

    placeholder: str
    description: Optional[str]


@dataclass
class ErrorCodeDetails:
    """
    Error code details according to schema specification.
    https://schemas.exasol.com/error_code_report-1.0.0.json
    """

    identifier: str
    message: Optional[str]
    messagePlaceholders: Optional[List[Placeholder]]
    description: Optional[str]
    internalDescription: Optional[str]
    potentialCauses: Optional[List[str]]
    mitigations: Optional[List[str]]
    sourceFile: Optional[str]
    sourceLine: Optional[int]
    contextHash: Optional[str]


class Validation:
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


class _ExaErrorNodeWalker:
    @staticmethod
    def _is_exa_error(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        name = getattr(node.func, "id", "")
        name = getattr(node.func, "attr", "") if name == "" else name
        return name == "ExaError"

    def __init__(self, root_node: ast.AST):
        self._root = root_node

    def __iter__(self) -> Generator[ast.Call, None, None]:
        return (
            node
            for node in ast.walk(self._root)
            if _ExaErrorNodeWalker._is_exa_error(node) and isinstance(node, ast.Call)
        )


class _Validator:
    def __init__(self):
        self._warnings: List[Validation.Warning] = list()
        self._errors: List[Validation.Error] = list()
        self._error_msg = "{type} only can contain constant values, details: {value}"

    @property
    def errors(self) -> Iterable[Validation.Error]:
        return self._errors

    @property
    def warnings(self) -> Iterable[Validation.Warning]:
        return self._warnings

    def validate(
        self, node: ast.Call, file: str
    ) -> Tuple[List[Validation.Error], List[Validation.Warning]]:
        code: ast.Constant
        message: ast.Constant
        mitigations: Union[ast.Constant, ast.List]
        parameters: ast.Dict
        code, message, mitigations, parameters = node.args

        # TODO: Add/Collect additional warnings:
        #        * error message/mitigation defines a placeholder, but no parameter is provided
        #        * error defines a parameter, but it is never used
        # TODO: Add/Collect additional errors:
        #        * check for invalid error code format
        #
        # see also, issue #<TBD>

        # make sure all parameters have the valid type
        self._validate_code(code, file)
        self._validate_message(message, file)
        self._validate_mitigations(mitigations, file)
        self._validate_parameters(parameters, file)

        return self._errors, self._warnings

    def _validate_code(self, code: ast.Constant, file: str):
        if not isinstance(code, ast.Constant):
            self._errors.append(
                Validation.Error(
                    message=self._error_msg.format(
                        type="error-codes", value=type(code)
                    ),
                    file=file,
                    line_number=code.lineno,
                )
            )

    def _validate_message(self, node: ast.Constant, file: str):
        if not isinstance(node, ast.Constant):
            self._errors.append(
                Validation.Error(
                    message=self._error_msg.format(type="message", value=type(node)),
                    file=file,
                    line_number=node.lineno,
                )
            )

    def _validate_mitigations(self, node: Union[ast.Constant, ast.List], file: str):
        if not isinstance(node, ast.List) and not isinstance(node, ast.Constant):
            self._errors.append(
                Validation.Error(
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
                    Validation.Error(
                        message=self._error_msg.format(
                            type="mitigations", value=type(e)
                        ),
                        file=file,
                        line_number=e.lineno,
                    )
                    for e in invalid
                ]
            )

    def _validate_parameters(self, node: ast.Dict, file: str):
        # Validate parameters
        for key in node.keys:
            if not isinstance(key, ast.Constant):
                self._errors.append(
                    Validation.Error(
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
                        Validation.Error(
                            message=self._error_msg.format(
                                type="description", value=type(description)
                            ),
                            file=file,
                            line_number=value.lineno,
                        )
                    )


class ErrorCollector:
    """ """

    def __init__(self, root: ast.AST, filename: str = "<Unknown>"):
        self._filename = filename
        self._root = root
        self._validator = _Validator()
        self._error_definitions: List[ErrorCodeDetails] = list()

    @property
    def error_definitions(self) -> List[ErrorCodeDetails]:
        return self._error_definitions

    @property
    def errors(self) -> Iterable[Validation.Error]:
        return self._validator.errors

    @property
    def warnings(self) -> Iterable[Validation.Warning]:
        return self._validator.warnings

    def _make_error(self, node: ast.Call) -> ErrorCodeDetails:
        code: ast.Constant
        message: ast.Constant
        mitigations: Union[ast.List, ast.Constant]
        parameters: ast.Dict
        code, message, mitigations, parameters = node.args

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
            mitigations=[m.value for m in mitigations.elts]
            if not isinstance(mitigations, str)
            else [mitigations],
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


class _JsonEncoder(json.JSONEncoder):
    """Json encoder with dataclass support"""

    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)


def _parse_file(
    file: Union[str, Path, io.FileIO]
) -> Tuple[
    Iterable[ErrorCodeDetails], Iterable[Validation.Warning], Iterable[Validation.Error]
]:
    with ExitStack() as stack:
        f = (
            file
            if isinstance(file, io.TextIOBase)
            else stack.enter_context(open(file, "r"))
        )
        root_node = ast.parse(f.read())
        collector = ErrorCollector(root_node, f.name)
        collector.collect()

        return collector.error_definitions, collector.warnings, collector.errors


def parse_command(args: argparse.Namespace) -> ExitCode:
    """Parse errors out one or more python files and report them in the jsonl format."""
    for f in args.python_file:
        definitions, warnings, errors = _parse_file(f)
        for d in definitions:
            print(json.dumps(d, cls=_JsonEncoder))
        for w in warnings:
            print(w, file=sys.stderr)
        if errors:
            print("\n".join(str(e) for e in errors), file=sys.stderr)
            return ExitCode.FAILURE

    return ExitCode.SUCCESS


def generate_command(args: argparse.Namespace) -> ExitCode:
    """Generate an error code file for the specified workspace


    Improvements, future TODO's (see issue#<to be created>):

        Add support for:
        * Derive python files from pyproject.toml package definition
        * Derive name form pyproject.toml
        * Derive version from pyproject.toml
    """

    def _report(project_name, project_version, errors):
        return {
            "$schema": "https://schemas.exasol.com/error_code_report-1.0.0.json",
            "projectName": project_name,
            "projectVersion": project_version,
            "errorCodes": [e for e in errors],
        }

    all_definitions = list()
    all_warnings = list()
    paths = [Path(p) for p in args.root]
    files = {f for f in chain.from_iterable([root.glob("**/*.py") for root in paths])}
    for f in files:
        definitions, warnings, errors = _parse_file(f)

        if errors:
            print("\n".join(str(e) for e in errors), file=sys.stderr)
            return ExitCode.FAILURE

        all_definitions.extend(definitions)
        all_warnings.extend(warnings)

    for w in all_warnings:
        print(w, file=sys.stderr)
    error_catalogue = _report(args.name, args.version, all_definitions)
    print(json.dumps(error_catalogue, cls=_JsonEncoder))

    return ExitCode.SUCCESS


def _argument_parser():
    parser = argparse.ArgumentParser(
        prog="ec",
        description="Error Crawler",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug", action="store_true", help="Do not protect main entry point."
    )
    subparsers = parser.add_subparsers()

    parse = subparsers.add_parser(
        name="parse",
        description="parses error definitions out of python files and reports them in jsonl format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parse.add_argument(
        "python_file",
        metavar="python-file",
        type=argparse.FileType("r"),
        default=[sys.stdin],
        nargs="*",
        help="file to parse",
    )
    parser.set_defaults(func=parse_command)

    generate = subparsers.add_parser(
        name="generate",
        description="Generate an error code report for a project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    generate.add_argument(
        "name",
        metavar="name",
        type=str,
        help="of the project which will be in the report",
    )
    generate.add_argument(
        "version",
        metavar="version",
        type=str,
        help="which shall be in the report. Should be in the following format 'MAJOR.MINOR.PATCH'",
    )
    generate.add_argument(
        "root",
        metavar="root",
        type=Path,
        default=[Path(".")],
        nargs="*",
        help="to start recursively fetching python files from",
    )
    generate.set_defaults(func=generate_command)

    return parser


def main():
    parser = _argument_parser()
    args = parser.parse_args()

    def _unprotected(func, *args, **kwargs):
        sys.exit(func(*args, **kwargs))

    def _protected(func, *args, **kwargs):
        try:
            sys.exit(func(*args, **kwargs))
        except Exception as ex:
            print(
                f"Error occurred, details: {ex}. Try running with --debug to get more details."
            )
            sys.exit(ExitCode.FAILURE)

    if args.debug:
        _unprotected(args.func, args)
    else:
        _protected(args.func, args)
