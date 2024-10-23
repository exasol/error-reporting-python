.. _user_guide:

:octicon:`person` User Guide
============================

This project contains a Python library for describing Exasol error messages.
This library lets you define errors with a uniform set of attributes.
Furthermore, the error message is implemented to be parseable,
so that you can extract an error catalog from the code.

Error Objects
~~~~~~~~~~~~~

Error objects are built using the function :code:`ExaError`.
Please keep in mind that error-code should satisfy the error-code format (see `code`_).

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

Check out the `user guide <doc/user_guide/user_guide.md>`_ for more details.

Tooling
~~~~~~~

The :code:`exasol-error-reporting` library comes with a command line tool (:code:`ec`) which also can be invoked by using its package/module entry point (:code:`python -m exasol.error._cli`). For detailed information about the usage consider consulting the help :code:`ec --help` or :code:`python -m exasol.error._cli --help`.

Parsing the error definitions in a python file(s)
-------------------------------------------------

.. code-block:: shell

    ec parse some-python-file.py 

.. code-block:: shell

    ec parse < some-python-file.py 

Generating an error-code data file
----------------------------------

In order to generate a `error-code-report <https://schemas.exasol.com/error_code_report-1.0.0.json>`_ compliant data file, you can use the generate subcommand.

.. code-block:: shell

    ec generate NAME VERSION PACKAGE_ROOT > error-codes.json

Information for Users
---------------------

* `User Guide <doc/user_guide/user_guide.md>`_
* `Changelog <doc/changes/changelog.md>`_

You can find corresponding libraries for other languages here:
* `Error reporting Java <https://github.com/exasol/error-reporting-java>`_
* `Error reporting Lua <https://github.com/exasol/error-reporting-lua>`_
* `Error reporting Go <https://github.com/exasol/error-reporting-go>`_
* `Error reporting C# <https://github.com/exasol/error-reporting-csharp>`_

Information for Contributors
----------------------------

* `System Requirement Specification <doc/system_requirements.md>`_
* `Design <doc/design.md>`_
* `Dependencies <doc/dependencies.md>`_
