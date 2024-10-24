.. _tools:

:octicon:`terminal` Tools
=========================

The error-reporting-python library comes with a set of command-line tools to assist working with error definitions. The main entry point of these tools is the :code:`ec` command.

How to get Help
---------------

.. code-block:: shell

     $ ec --help

.. code-block:: shell

     $ ec parse --help

.. code-block:: shell

     $ ec generate --help

Example Usages
--------------

Parsing the error definitions in a python file(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    ec parse some-python-file.py 
    
.. code-block:: shell
    
    ec parse < some-python-file.py 

Generating an error-code data file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to generate a `error-code-report <https://schemas.exasol.com/error_code_report-1.0.0.json>`__ compliant data file,
you can use the generate subcommand.

.. code-block:: shell

    ec generate NAME VERSION PACKAGE_ROOT > error-codes.json
