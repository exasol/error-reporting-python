"""Configuration for nox based task runner"""

from __future__ import annotations

from dataclasses import dataclass
from exasol.toolbox.nox.plugin import hookimpl
from pathlib import Path
from typing import Iterable


class UpdateErrorCodes:
    ERROR_CODES: Path = Path(__file__).parent / "error-codes.json"

    @hookimpl
    def prepare_release_update_version(self, session, config, version):
        import json

        from exasol.error._error import _create_error_code_definitions

        definitions = _create_error_code_definitions(f"{version}")
        with open(UpdateErrorCodes.ERROR_CODES, "w") as f:
            json.dump(definitions, f)

    @hookimpl
    def prepare_release_add_files(self, session, config):
        return [self.ERROR_CODES]


@dataclass(frozen=True)
class Config:
    """Project specific configuration used by nox infrastructure"""

    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    source: Path = Path("exasol/error")
    version_file: Path = Path(__file__).parent / "exasol" / "error" / "version.py"
    python_versions = ["3.9", "3.10", "3.11", "3.12", "3.13"]
    path_filters: Iterable[str] = ("dist", ".eggs", "venv")
    plugins = [UpdateErrorCodes]


PROJECT_CONFIG = Config()
