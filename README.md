# Exasol Error Reporting

This project contains a Python library for describing Exasol error messages.
This library lets you define errors with a uniform set of attributes.
Furthermore, the error message is implemented to be parseable,
so that you can extract an error catalog from the code.

## In a Nutshell

### Install the library

```shell
pip install exasol-error-reporting
```

### Create a Simple Error

```python
from exasol import error

error1 = error.ExaError(
    "E-TEST-1", "A trivial error", "No mitigation available", {}
)
```

### Specify Multiple Mitigations
```python
from exasol import error

error2 = error.ExaError(
    "E-TEST-2",
    message="Fire in the server room",
    mitigations=[
        "Use the fire extinguisher",
        "Flood the room with halon gas (Attention: make sure no humans are in the room!)"
    ],
    parameters={}
)
```

### Error Parameter(s) without description

```python
from exasol import error

error3 = error.ExaError(
    "E-TEST-2",
    "Not enough space on device {{device}}.",
    "Delete something from {{device}}.",
    {"device": "/dev/sda1"},
)
```
### Error with detailed Parameter(s) 

```python
from exasol import error
from exasol.error import Parameter

error4 = error.ExaError(
    "E-TEST-2",
    "Not enough space on device {{device}}.",
    "Delete something from {{device}}.",
    {"device": Parameter("/dev/sda1", "name of the device")},
)
```

Check out the [user guide](doc/user_guide/user_guide.md) for more details.

## Tooling

The `exasol-error-reporting` library comes with a command line tool (`ec`) which also can be invoked
by using its package/module entry point (`python -m exasol.error`).
For detailed information about the usage consider consulting the help `ec --help` or `python -m exasol.error --help`.

### Parsing the error definitions in a python file(s)

```shell
ec parse some-python-file.py 
```

```shell
ec parse < some-python-file.py 
```

## Generating an error-code data file

In order to generate a [error-code-report](https://schemas.exasol.com/error_code_report-1.0.0.json) compliant data file,
you can use the generate subcommand.

```shell
ec generate NAME VERSION PACKAGE_ROOT > error-codes.json
```


## Links and References

For further details check out the [project documentation](https://exasol.github.io/error-reporting-python/).
