.. _user_guide:

:octicon:`person` User Guide
============================

This project provides a Python library for defining Exasol-compliant errors. Additionally, the defined errors can be parsed, allowing you to extract an error catalog from the code.

Error Objects
~~~~~~~~~~~~~

Error objects are built using the function :code:`ExaError`.
Please keep in mind that an error-code should satisfy the error-code format (see `code`_).

Flexibility is provided by introducing placeholder parameters to the error message.

code
----

This parameter needs to obey the following format (:code:`^[FEW]-[[A-Z][A-Z0-9]+(-[A-Z][A-Z0-9]+)*-[0-9]+$`):

``severity "-" project-short-tag ["-" module-short-tag] "-" error-number`` where:

- *severity*: either F (Failure, not recoverable), or E (Error, recoverable), or W (warning),
- *project-short-tag*: alphanumeric starting with an alphabet.
- *module-short-tag*: alphanumeric starting with an alphabet.
- *error-number*: only number.

Examples of valid error codes:

- E-EXA-22004
- E-EXA-SQL-22004
- F-VS-QRW-13

message
-------

This parameter includes the error description which can be given by either a static string or a string containing placeholders in double curly brackets. Parameters of placeholders in the error message can be provided using the :code:`parameters` parameter.

mitigations
-----------

This parameter provides a list of hints on how to fix the error.
Parameters of placeholders in the mitigations can be given via the :code:`parameters` parameter.

parameters
----------

This argument takes a dictionary of placeholder names and the respective parameter values.
They will be used to replace the placeholders in the mitigations and messages.

Usage
~~~~~

Install the library
-------------------

.. code-block:: shell

    pip install exasol-error-reporting

Create a Simple Error
---------------------

.. code-block:: python

    from exasol import error

    error1 = error.ExaError(
        "E-TEST-1", "A trivial error", "No mitigation available", {}
    )

Specify Multiple Mitigations
----------------------------

.. code-block:: python

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

Error Parameter(s) without description
--------------------------------------

.. code-block:: python

    from exasol import error

    error3 = error.ExaError(
        "E-TEST-2",
        "Not enough space on device {{device}}.",
        "Delete something from {{device}}.",
        {"device": "/dev/sda1"},
    )

Error with detailed Parameter(s)
--------------------------------

.. code-block:: python

    from exasol import error
    from exasol.error import Parameter

    error4 = error.ExaError(
        "E-TEST-2",
        "Not enough space on device {{device}}.",
        "Delete something from {{device}}.",
        {"device": Parameter("/dev/sda1", "name of the device")},
    )

Tooling
~~~~~~~

The :code:`exasol-error-reporting` library includes command-line tools to manage and work with error definitions. For further details, see the :ref:`tools` section of the documentation.

Links & References
~~~~~~~~~~~~~~~~~~

* `Error Code Report Schemas <https://schemas.exasol.com>`_
* `Error reporting Java <https://github.com/exasol/error-reporting-java>`_
* `Error reporting Lua <https://github.com/exasol/error-reporting-lua>`_
* `Error reporting Go <https://github.com/exasol/error-reporting-go>`_
* `Error reporting C# <https://github.com/exasol/error-reporting-csharp>`_

