# Error Reporting Python

This project contains a python library for describing Exasol error messages. 
This library lets you define errors with a uniform set of attributes. 
Furthermore, the error message  is implemented to be parseable, 
so that you can extract an error catalog from the code.


## In a Nutshell
Create an error object:

```python
exa_error_obj = ExaError.message_builder('E-TEST-1')\
    .message("Not enough space on device {{device}}.")\
    .mitigation("Delete something from {{device}}.")\
    .mitigation("Create larger partition.")\
    .parameter("device", "/dev/sda1", "name of the device") 
```

Use it as string:

```python
print(exa_error_obj)
```

Result:
```
E-TEST-1: Not enough space on device '/dev/sda1'. Known mitigations:
* Delete something from '/dev/sda1'.
* Create larger partition.
```


Check out the [user guide](doc/user_guide/user_guide.md) for more details.

### Information for Users

* [User Guide](doc/user_guide/user_guide.md)
* [Changelog](doc/changes/changelog.md)

You can find corresponding libraries for other languages here:

* [Error reporting Java](https://github.com/exasol/error-reporting-java)
* [Error reporting Lua](https://github.com/exasol/error-reporting-lua)
* [Error reporting Go](https://github.com/exasol/error-reporting-go)
* [Error reporting C#](https://github.com/exasol/error-reporting-csharp)

### Information for Contributors

* [System Requirement Specification](doc/system_requirements.md)
* [Design](doc/design.md)
* [Dependencies](doc/dependencies.md)