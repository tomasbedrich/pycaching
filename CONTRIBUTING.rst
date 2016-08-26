===============================================================================
Contributing
===============================================================================


First time
-------------------------------------------------------------------------------

1. Clone a repository from GitHub:

   .. code-block:: bash

       git clone https://github.com/tomasbedrich/pycaching.git
       cd pycaching

2. *Optional:* create a virtualenv:

   .. code-block:: bash

       python3 -m venv .
       source bin/activate  # Unix
       Scripts\activate  # Windows

3. Setup an enviroment:

   .. code-block:: bash

       python3 setup.py develop


Typical workflow
-------------------------------------------------------------------------------

1. Pick an issue labeled as `"contributors friendly"
   <https://github.com/tomasbedrich/pycaching/issues?q=is:open+is:issue+label:"contributors+friendly">`_
   or create a new one. **Notify others** that you will solve this problem (write a comment
   on GitHub).
2. *Optional:* Activate the virtualenv:

   .. code-block:: bash

       source bin/activate  # Unix
       Scripts\activate  # Windows


3. Write some **code and tests**. After that, don't forget to update the **docs**. See coding style
   below.
4. Run the linter and tests:

   .. code-block:: bash

       python3 setup.py lint test

   Make sure that:

   - there are no lint errors,
   - all tests are passing,
   - the coverage is above 95%.

5. Push your work and create a **pull request**. Yay!

Coding style
-------------------------------------------------------------------------------

- For code, follow `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_.

  - Use **double quotes**.
  - Try to keep line length below **100 characters** (or 120 if absolutely nescessary).
  - Use `.format()` for string formatting.

- For docs, please follow `PEP257 <https://www.python.org/dev/peps/pep-0257/>`_.
- **Importing modules** is okay for modules from standard library. If you want to include
  third-party module, please consult it on GitHub before.
- `Please use regular expressions only as a last resort. <http://imgur.com/j3G9xyP>`_ When possible, use string manipulations,
  such as :code:`split()` and then list operations. It is more readable.
