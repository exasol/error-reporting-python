.. _developer_guide:

:octicon:`tools` Developer Guide
================================

Creating a Release
++++++++++++++++++

Prepare the Release
-------------------

To prepare for a release, a pull request with the following parameters needs to be created:

- Updated version numbers
- Updated the changelog
- Updated workflow templates (not automated yet)

This can be achieved by running the following command:

.. code-block:: shell

   nox -s prepare-release -- <major>.<minor>.<patch>

Replace `<major>`, `<minor>`, and `<patch>` with the appropriate version numbers.
Once the PR is successfully merged, the release can be triggered (see next section).

Triggering the Release
----------------------

To trigger a release, a new tag must be pushed to GitHub. For further details, see `.github/workflows/ci-cd.yml`.

1. Create a local tag with the appropriate version number:

    .. code-block:: shell

        git tag x.y.z

2. Push the tag to GitHub:

    .. code-block:: shell

        git push origin x.y.z


What to do if the release failed?
---------------------------------

The release failed during pre-release checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Delete the local tag

    .. code-block:: shell

        git tag -d x.y.z

#. Delete the remote tag

    .. code-block:: shell

        git push --delete origin x.y.z

#. Fix the issue(s) which lead to the failing checks
#. Start the release process from the beginning


One of the release steps failed (Partial Release)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Check the Github action/workflow to see which steps failed
#. Finish or redo the failed release steps manually

.. note:: Example

    **Scenario**: Publishing of the release on Github was successfully but during the PyPi release, the upload step got interrupted.

    **Solution**: Manually push the package to PyPi



