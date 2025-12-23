.. _developer_guide:

:octicon:`tools` Developer Guide
================================

Preparing & Triggering a Release
********************************

The `exasol-toolbox` provides nox tasks to semi-automate the release process:

.. code-block:: python

    # prepare a release
    nox -s release:prepare -- --type {major,minor,patch}

    # trigger a release
    nox -s release:trigger

For further information, please refer to the `exasol-toolbox`'s page `How to Release
<https://exasol.github.io/python-toolbox/main/user_guide/features/creating_a_release.html>`_.


