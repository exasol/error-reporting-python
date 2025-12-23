"""Configuration for nox based task runner"""

from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from exasol.toolbox.nox.plugin import hookimpl


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


PROJECT_CONFIG = BaseConfig(
    root_path=Path(__file__).parent,
    project_name="error",
    python_versions=("3.10", "3.11", "3.12", "3.13"),
    plugins_for_nox_sessions=(UpdateErrorCodes,),
)
