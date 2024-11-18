# error-reporting-python 0.2.0, released 2022-03-28

Code Name: Eliminated the nested set warning caused by the error code format

## Summary

In this release, we eliminated the nested set warning caused by the error-code format. 
Furthermore, in case of having an invalid error code, ValueError is thrown instead of AssertError.

### Bug Fixes

  - #8: Eliminated nested set warning in error code format 

    