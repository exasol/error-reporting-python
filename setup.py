# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_error_reporting_python']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'exasol-error-reporting-python',
    'version': '0.1.0',
    'description': 'Exasol Python Error Reporting',
    'long_description': '# Error Reporting Python\n\nThis project contains a python library for describing Exasol error messages.',
    'author': 'Umit Buyuksahin',
    'author_email': 'umit.buyuksahin@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exasol/error-reporting-python',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
