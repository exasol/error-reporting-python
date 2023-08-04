import importlib
from collections import namedtuple
from contextlib import contextmanager
from inspect import cleandoc

import pytest

from exasol.error import ExaError, Parameter

Data = namedtuple("Data", ["code", "message", "mitigations", "parameters"])


@contextmanager
def does_not_raise():
    try:
        yield
    except Exception as ex:
        pytest.fail(f"Exception was raised where none is to be expected, details: {ex}")


@pytest.mark.parametrize(
    "expected,data",
    [
        (
            cleandoc(
                """
                        E-TEST-1: Not enough space on device '/dev/sda1'. Known mitigations:
                        * Delete something from '/dev/sda1'.
                        * Create larger partition.
                        """
            ),
            Data(
                code="E-TEST-1",
                message="Not enough space on device {{device}}.",
                mitigations=[
                    "Delete something from {{device}}.",
                    "Create larger partition.",
                ],
                parameters={"device": Parameter("/dev/sda1", "name of the device")},
            ),
        ),
        (
            cleandoc(
                """
                            E-TEST-1: Not enough space on device '/dev/sda1'. Known mitigations:
                            * Delete something from '/dev/sda1'.
                            * Create larger partition.
                            """
            ),
            Data(
                code="E-TEST-1",
                message="Not enough space on device {{device}}.",
                mitigations=[
                    "Delete something from {{device}}.",
                    "Create larger partition.",
                ],
                parameters={"device": "/dev/sda1"},
            ),
        ),
    ],
)
def test_exa_error_as_string(expected, data):
    error = ExaError(data.code, data.message, data.mitigations, data.parameters)
    actual = str(error)
    assert actual == expected


@pytest.mark.xfail(
    True,
    reason="Old implementation does not avoid throwing exceptions, further refactoring is needed.",
)
@pytest.mark.parametrize(
    "data",
    [
        (
            Data(
                code="BROKEN_ERROR_CODE",
                message='"Not enough space on device {{device}}."',
                mitigations=[
                    "Delete something from {{device}}.",
                    "Create larger partition.",
                ],
                parameters={"device": Parameter("/dev/sda1", "name of the device")},
            )
        ),
    ],
)
def test_exa_error_does_not_throw_error_on_invalid(data):
    with does_not_raise():
        _ = ExaError(data.code, data.message, data.mitigations, data.parameters)


def test_using_the_old_api_produces_deprecation_warning():
    with pytest.warns(DeprecationWarning):
        # due to the fact that the exasol.error package already imports the package at an earlier stage
        # we need to ensure the module is imported during the test itself.
        import exasol_error_reporting_python

        importlib.reload(exasol_error_reporting_python)
