import importlib
from collections import namedtuple
from contextlib import contextmanager
from inspect import cleandoc

import pytest

from exasol.error import (
    ExaError,
    Parameter,
)

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
        (
            cleandoc(
                "E-ERP-1: Invalid error code 'WRONGCODE'. Ensure you follow the standard error code format."
            ),
            Data(
                code="WRONGCODE",
                message="some error message",
                mitigations=["unrecoverable ;P"],
                parameters={},
            ),
        ),
    ],
)
def test_exa_error_as_string(expected, data):
    error = ExaError(data.code, data.message, data.mitigations, data.parameters)
    actual = str(error)
    assert actual == expected


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


@pytest.mark.parametrize(
    "data",
    [
        Data(
            code="E-TEST-1",
            message="some error message",
            mitigations=["unrecoverable ;P"],
            parameters={},
        ),
    ],
)
def test_raising_message_builder(data):
    from unittest.mock import patch

    from exasol.error.exa_error import ExaError as Error

    actual_impl = Error.message_builder

    def builder(error_code):
        if error_code == "E-ERP-2":
            return actual_impl(error_code)
        raise Exception(f"{error_code}")

    with patch("exasol.error.exa_error.ExaError") as mock:
        mock.message_builder = builder
        error = ExaError(data.code, data.message, data.mitigations, data.parameters)
    actual = str(error)
    expected = cleandoc(
        """
        E-ERP-2: Unknown error/exception occurred. A good starting point would be to investigate the cause of the attached exception.

        Trackback:
    """
    )
    assert expected in actual
