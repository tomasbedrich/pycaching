===============================================================================
Contributing
===============================================================================


First time
-------------------------------------------------------------------------------

1. Clone a repository from GitHub:

   .. code-block:: bash

       git clone https://github.com/tomasbedrich/pycaching.git
       cd pycaching

2. Create a virtualenv:

   .. code-block:: bash

       python3 -m venv .venv
       source .venv/bin/activate  # Unix
       .venv\Scripts\activate  # Windows

3. Install `Flit <https://flit.readthedocs.io/en/latest/>`_:

   .. code-block:: bash

       pip install flit

4. Install Pycaching package + dependencies in development mode:

   .. code-block:: bash

       flit install --symlink


Typical workflow
-------------------------------------------------------------------------------

1. Pick an issue labeled as `"contributors friendly"
   <https://github.com/tomasbedrich/pycaching/issues?q=is:open+is:issue+label:"contributors+friendly">`_
   or create a new one. Please **notify others** that you will solve this problem (write a comment
   on GitHub).

2. Activate the virtualenv:

   .. code-block:: bash

       source .venv/bin/activate  # Unix
       .venv\Scripts\activate  # Windows

3. Write some **code and tests**. After that, don't forget to update the **docs**. See coding style below.

4. Sort imports using `isort <https://pycqa.github.io/isort/>`_,
   format the code using `Black <https://black.readthedocs.io/en/stable/>`_,
   lint it using `Flake <https://flake8.pycqa.org/>`_ and
   run the tests using `pytest <https://docs.pytest.org/>`_:

   .. code-block:: bash

       isort .
       black .
       flake8
       pytest

   Make sure that:

   - there are no lint errors,
   - all tests are passing,
   - the coverage is above 90%.

6. Push your work and create a **pull request**. Yay!


Testing
-------------------------------------------------------------------------------

Pycaching uses `Betamax <https://betamax.readthedocs.io/en/latest/>`__ for testing, which speeds
it up by recording network requests so that they can be mocked.

If you haven't written or modified any tests, tests can be run just like:

.. code-block:: bash

    pytest <test folder name>

If you have written or modified tests, you must provide a username and password for testing. Don't
worry, these will not leave your computer. Betamax will insert a placeholder when it records any
new cassettes. To run new tests, first set up the following environment variables:

.. code-block:: bash

    PYCACHING_TEST_USERNAME="yourusername" PYCACHING_TEST_PASSWORD="yourpassword" pytest <test folder name>

Substitute your username for ``yourusername`` and your password for ``yourpassword``.
This requires you to use a basic member account, otherwise you might see unexpected test failures.

To re-record a specific cassette in case of site changes, delete the corresponding JSON file and
provide username and password as explained above. The missing cassette will be recorded for future
usages.


Coding style
-------------------------------------------------------------------------------

- Use `.format()` for string formatting. Black will guide you with the rest. :)
- For docs, please follow `PEP257 <https://www.python.org/dev/peps/pep-0257/>`_.
- **Importing modules** is okay for modules from standard library. If you want to include a
  third-party module, please consult it on GitHub before.
- `Please use regular expressions only as a last resort. <http://imgur.com/j3G9xyP>`_ When possible, use string manipulations,
  such as :code:`split()` and then list operations. It is more readable.


Release process
-------------------------------------------------------------------------------

1. Pick a suitable semantic version number. We adhere to `generic rules <https://docs.npmjs.com/about-semantic-versioning#incrementing-semantic-versions-in-published-packages>`_ with an exception of our `specific deprecation policy <https://github.com/tomasbedrich/pycaching/blob/master/docs/api.rst?plain=1#L7-L11>`_.
2. If the deprecation policy triggers, remove the deprecated methods. Create a separate PR in that case.
3. Bump the version number in ``pycaching/__init__.py`` (`example <https://github.com/tomasbedrich/pycaching/commit/1824668110a58afa7085744d975e9c6f3ab6b35f>`_). Feel free to push this bump directly to ``master``, or create a regular PR.
4. Once the version bump commit equals HEAD of ``master``, `draft a new release <https://github.com/tomasbedrich/pycaching/releases/new>`_ using Github. Using that form, create a new tag corresponding to the version number (no prefixes). Leave release title empty, let Github generate the release notes. Update release notes manually if needed.
5. Publish the Github release. There is a Github action which publishes the release to Pypi. There are Webhooks which update Readthedocs and Coveralls.

Should there be any issue with the above (most likely stuck release pipeline), please create a Github issue.
