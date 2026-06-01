import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYMODULE_CONTENT = """from exasol import error
from exasol.error import Parameter
error1 = error.ExaError(
  "E-TEST-1",
  "this is an error",
  ["no mitigation available"],
  {"param": Parameter("value", "some description")},
)
error2 = error.ExaError(
  "E-TEST-2", "this is an error", ["no mitigation available"], {"param": "value"}
)
"""
EXPECTED_ERRORS = [
    {
        "identifier": "E-TEST-1",
        "message": "this is an error",
        "messagePlaceholders": [
            {"placeholder": "param", "description": "some description"}
        ],
        "description": None,
        "internalDescription": None,
        "potentialCauses": None,
        "mitigations": ["no mitigation available"],
        "sourceFile": "pymodule.py",
        "sourceLine": 3,
        "contextHash": None,
    },
    {
        "identifier": "E-TEST-2",
        "message": "this is an error",
        "messagePlaceholders": [{"placeholder": "param", "description": ""}],
        "description": None,
        "internalDescription": None,
        "potentialCauses": None,
        "mitigations": ["no mitigation available"],
        "sourceFile": "pymodule.py",
        "sourceLine": 9,
        "contextHash": None,
    },
]


def _env():
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{pythonpath}" if pythonpath else str(REPO_ROOT)
    )
    return env


def _run(command: list[str], *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*command, "--debug", *args],
        cwd=cwd,
        env=_env(),
        check=True,
        capture_output=True,
        text=True,
    )


def _commands():
    yield pytest.param([sys.executable, "-m", "exasol.error"], id="module-entrypoint")
    ec_path = shutil.which("ec")
    if ec_path:
        yield pytest.param([ec_path], id="console-script")
    else:
        yield pytest.param(
            [sys.executable, "-c", "from exasol.error._cli import main; main()"],
            id="cli-module-fallback",
        )


@pytest.fixture
def sample_module(tmp_path: Path) -> Path:
    module = tmp_path / "pymodule.py"
    module.write_text(PYMODULE_CONTENT, encoding="utf-8")
    return module


@pytest.mark.parametrize("command", _commands())
def test_parse_subcommand(command: list[str], sample_module: Path):
    result = _run(command, "parse", sample_module.name, cwd=sample_module.parent)

    assert result.stderr == ""
    assert [json.loads(line) for line in result.stdout.splitlines()] == EXPECTED_ERRORS


@pytest.mark.parametrize("command", _commands())
def test_generate_subcommand(command: list[str], sample_module: Path):
    result = _run(
        command, "generate", "modulename", "1.2.0", ".", cwd=sample_module.parent
    )

    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "$schema": "https://schemas.exasol.com/error_code_report-1.0.0.json",
        "projectName": "modulename",
        "projectVersion": "1.2.0",
        "errorCodes": EXPECTED_ERRORS,
    }
