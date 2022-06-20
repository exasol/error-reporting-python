# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_error_reporting_python']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'exasol-error-reporting-python',
    'version': '0.2.0',
    'description': 'Exasol Python Error Reporting',
    'long_description': '# Error Reporting Python\n\nThis project contains a python library for describing Exasol error messages. \nThis library lets you define errors with a uniform set of attributes. \nFurthermore, the error message  is implemented to be parseable, \nso that you can extract an error catalog from the code.\n\n\n## In a Nutshell\nCreate an error object:\n\n```python\nexa_error_obj = ExaError.message_builder(\'E-TEST-1\')\\\n    .message("Not enough space on device {{device}}.")\\\n    .mitigation("Delete something from {{device}}.")\\\n    .mitigation("Create larger partition.")\\\n    .parameter("device", "/dev/sda1", "name of the device") \n```\n\nUse it as string:\n\n```python\nprint(exa_error_obj)\n```\n\nResult:\n```\nE-TEST-1: Not enough space on device \'/dev/sda1\'. Known mitigations:\n* Delete something from \'/dev/sda1\'.\n* Create larger partition.\n```\n\n\nCheck out the [user guide](doc/user_guide/user_guide.md) for more details.\n\n### Information for Users\n\n* [User Guide](doc/user_guide/user_guide.md)\n* [Changelog](doc/changes/changelog.md)\n\nYou can find corresponding libraries for other languages here:\n\n* [Error reporting Java](https://github.com/exasol/error-reporting-java)\n* [Error reporting Lua](https://github.com/exasol/error-reporting-lua)\n* [Error reporting Go](https://github.com/exasol/error-reporting-go)\n* [Error reporting C#](https://github.com/exasol/error-reporting-csharp)\n\n### Information for Contributors\n\n* [System Requirement Specification](doc/system_requirements.md)\n* [Design](doc/design.md)\n* [Dependencies](doc/dependencies.md)',
    'author': 'Umit Buyuksahin',
    'author_email': 'umit.buyuksahin@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exasol/error-reporting-python',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
