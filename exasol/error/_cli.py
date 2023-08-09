import argparse
import json
import sys
from enum import IntEnum
from itertools import chain
from pathlib import Path

from exasol.error._parse import parse_file
from exasol.error._report import JsonEncoder


class ExitCode(IntEnum):
    SUCCESS = 0
    FAILURE = -1


def parse_command(args: argparse.Namespace) -> ExitCode:
    """Parse errors out one or more python files and report them in the jsonl format."""
    for f in args.python_file:
        definitions, warnings, errors = parse_file(f)
        for d in definitions:
            print(json.dumps(d, cls=JsonEncoder))
        for w in warnings:
            print(w, file=sys.stderr)
        if errors:
            print("\n".join(str(e) for e in errors), file=sys.stderr)
            return ExitCode.FAILURE

    return ExitCode.SUCCESS


def generate_command(args: argparse.Namespace) -> ExitCode:
    """Generate an error code file for the specified workspace

    TODO: Improve command by reflecting information from pyproject.toml file
        * Derive python files from pyproject.toml package definition
        * Derive name form pyproject.toml
        * Derive version from pyproject.toml

        see also [Github Issue #24](https://github.com/exasol/error-reporting-python/issues/24)
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
        definitions, warnings, errors = parse_file(f)

        if errors:
            print("\n".join(str(e) for e in errors), file=sys.stderr)
            return ExitCode.FAILURE

        all_definitions.extend(definitions)
        all_warnings.extend(warnings)

    for w in all_warnings:
        print(w, file=sys.stderr)
    error_catalogue = _report(args.name, args.version, all_definitions)
    print(json.dumps(error_catalogue, cls=JsonEncoder))

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
