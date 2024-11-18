from exasol.error._error import Error
import pytest

@pytest.mark.parametrize(
    "error, fmt, expected",
    [
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "",
                ""
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "unknown",
                ""
        ),
        (
             Error(
                code="E-TEST-1",
                message="Not enough space on device {/dev/sda1}.",
                mitigations=[
                    "Delete something from {/dev/sda1}",
                    "Create larger partition."
                ],
                parameters={
                    "device": '/dev/sda1'
                }
            ),
            "long",
            "E-TEST-1 ['Not enough space on device {/dev/sda1}.'] ['Delete something from {/dev/sda1}', 'Create larger partition.'] {'device': '/dev/sda1'}"
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "short",
                "E-TEST-1 ['Not enough space on device {/dev/sda1}.']"
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "name",
                "E-TEST-1"
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "message",
                "['Not enough space on device {/dev/sda1}.']"
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "mitigations",
                "['Delete something from {/dev/sda1}', 'Create larger partition.']"
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "parameters",
                "{'device': '/dev/sda1'}"
        ),
        (
                Error(
                    code="E-TEST-1",
                    message="Not enough space on device {/dev/sda1}.",
                    mitigations=[
                        "Delete something from {/dev/sda1}",
                        "Create larger partition."
                    ],
                    parameters={
                        "device": '/dev/sda1'
                    }
                ),
                "parameters mitigations message name",
                "{'device': '/dev/sda1'} ['Delete something from {/dev/sda1}', 'Create larger partition.'] ['Not enough space on device {/dev/sda1}.'] E-TEST-1"
        ),
    ]
)
def test_fmt(error, fmt, expected):
    fmt_str = f"{{error:{fmt}}}"
    actual = fmt_str.format(error=error)
    assert actual == expected
