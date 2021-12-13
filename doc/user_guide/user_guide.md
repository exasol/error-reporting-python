# User Guide

This project contains a python library for describing Exasol error messages. 
This library lets you define errors with a uniform set of attributes. 
Furthermore, the error message  is implemented to be parseable, 
so that you can extract an error catalog from the code.

## Attributes of Error Builder

Error messages are built in `ExaError` using the following predefined attributes. 
All attributes of the error object except the error code are optional. Thus, the 
`ExaError` will still work, even if the other attributes are not provided. Please 
keep in mind that error-code should satisfy error-code format 
(see [error-code](#error-code)).

Flexibility is provided by introducing placeholder parameters to the error 
message in two ways: (1) via the `parameter` attribute and (2) with positional 
arguments. Furthermore, placeholders without parameters are filled with <null>.

#### error-code
This attribute should be defined in the error message and provide the following 
pattern (`^[FEW]-[[A-Z][A-Z0-9]+(-[A-Z][A-Z0-9]+)*-[0-9]+$`):

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
This attribute includes error description which can be given by either a static
string or a string containing placeholders in double curly brackets. Parameters 
of placeholders in the error message can be given as positional arguments 
as well as using the `parameter` attribute. The following two usages result in 
the same message (`Error message with value`):
- `.message("Error message with {{parameter}}", "value")`
- `.message("Error message with {{parameter}}").parameter("parameter", "value")`

Furthermore, multiple calls of the `message` method will append the corresponding 
message to the previous ones.

#### mitigation
This attribute provides a list of hints on how to fix the error. Its method 
structure is the same as for the `message` attribute. Parameters of placeholders 
in the mitigations can be given as positional arguments  as well as using the 
`parameter` attribute. Similar to the `message` method, multiple calls of 
the `mitigation` method will append the corresponding mitigation to the 
previous ones.
 
Furthermore, if the only message we can give is to open a ticket, the 
`ticket mitigation()` method can be called, which provides a predefined message 
about it.
   
#### parameter
This attribute takes the placeholder name and the parameter value 
that will replace this placeholder as argument. It can be used for both message 
and mitigations. For example usages, please see the 
[Parameters](#Parameters) section.

## Usage 

### Simple Messages
```python
ExaError.message_builder("E-TEST-1").message("Something went wrong.")
```
The result of the error message:
```
E-TEST-1: Something went wrong.
```


### Parameters
You can specify placeholders in the message and replace them with 
parameters values.

```python
ExaError.message_builder("E-TEST-2")
    .message("Unknown input: {{input}}.")
    .parameter("input", "unknown", "The illegal user input.")
```
or inline: 
```python
ExaError.message_builder("E-TEST-2")
    .message("Unknown input: {{input}}.",  "unknown")
```
The result of both error messages is same:
```
E-TEST-2: Unknown input: 'unknown'.
```

The optional third argument for `parameter(name, value, description)` 
method is used to generate a parameter description for the error-catalog.

The builder automatically quotes parameters (depending on the type of the 
parameter). If you don't want that, use the `|uq` suffix in the corresponding 
placeholder, as follows:

```python
ExaError.message_builder("E-TEST-2")
    .message("Unknown input: {{input|uq}}.")
    .parameter("input", "unknown", "The illegal user input.")
```
The result of the error message:
```
E-TEST-2: Unknown input: unknown.
```

### Mitigations
The mitigations describe actions the user can take to resolve the error. 
Here is an example of a mitigation definition:

```python
ExaError.message_builder("E-TEST-2")
    .message("Not enough space on device.")
    .mitigation("Delete something.")
```
The result of the error message:
```
E-TEST-2: Not enough space on device. Delete something.
```

You can use parameters in mitigations too.
```python
ExaError.message_builder("E-TEST-2")
    .message("Not enough space on device {{device}}.")
    .mitigation("Delete something from {{device}}.")
    .parameter("device", "/dev/sda1", "name of the device")
```
The result of the error message:
```
E-TEST-2: Not enough space on device '/dev/sda1'. Delete something from '/dev/sda1'.
```

You can chain `mitigation` definitions if you want to tell the users that there 
is more than one solution, as follows:
```python
ExaError.message_builder("E-TEST-2")
    .message("Not enough space on device.")
    .mitigation("Delete something.")
    .mitigation("Create larger partition.")
```
The result of the error message:
```
E-TEST-2: Not enough space on device. Known mitigations:
* Delete something.
* Create larger partition.
```