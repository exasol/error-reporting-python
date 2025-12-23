# Unreleased

## Refactoring

* #72: Dropped support for Python 3.9 as EOL was 2025-10, which newer dependencies no longer support

## Internal

* #68: Updated to poetry 2.1.2 and exasol-toolbox 1.1.0
* Updated transitive dependencies
* #67: Extended unit test to contain test scenarios with different values for the parameter description
* #72: Relocked transitive dependencies pip, urllib3, and filelock and updated exasol-toolbox to 4.0.0