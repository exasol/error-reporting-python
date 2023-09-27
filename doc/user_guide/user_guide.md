# User Guide

This project contains a python library for describing Exasol error messages. 
This library lets you define errors with a uniform set of attributes. 
Furthermore, the error message  is implemented to be parseable, 
so that you can extract an error catalog from the code.

## Creating an Error Object

Error objects are built using the function `ExaError`. 
Please keep in mind that error-code should satisfy the error-code format (see [code](#code)).

Flexibility is provided by introducing placeholder parameters to the error 
message.

#### code
This parameter needs to obey the following format (`^[FEW]-[[A-Z][A-Z0-9]+(-[A-Z][A-Z0-9]+)*-[0-9]+$`):

`severity "-" project-short-tag ["-" module-short-tag] "-" error-number` where,
- _severity_: either F (Failure, not recoverable), or E (Error, recoverable), 
or W (warning),
- _project-short-tag_: alphanumeric starting with alphabet.
- _module-short-tag_: alphanumeric starting with alphabet.
- _error-number_: only number.

Examples of valide error codes:
- E-EXA-22004
- E-EXA-SQL-22004
- F-VS-QRW-13

#### message
This parameter includes the error description which can be given by either a static
string or a string containing placeholders in double curly brackets. Parameters 
of placeholders in the error message can be provided using the `parameters` parameter.

#### mitigations
This parameter provides a list of hints on how to fix the error. 
Parameters of placeholders in the mitigations can be given via the `parameters` parameter.
 
#### parameters
This argument takes a dictionary of placeholder names and the respective parameter values.
They will be used to replace the placeholders in the mitigations and messages.
