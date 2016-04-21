===============================================================================
Contributing
===============================================================================


First time
-------------------------------------------------------------------------------

1. clone a repository from GitHub:

   .. code-block:: bash

       git clone https://github.com/tomasbedrich/pycaching.git
       cd pycaching

2. setup the enviroment

   .. code-block:: bash

       python3 setup.py develop


Workflow in a nutshell
-------------------------------------------------------------------------------

1. Pick an issue with `contributors friendly
   <https://github.com/tomasbedrich/pycaching/issues?q=is:open+is:issue+label:"contributors+friendly">`_
   label and write a comment about your choice on GitHub.
2. Write some code and tests. Follow `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ with
   **double quotes** and line length of **100 characters** (or 120 if absolutely nescessary).
   Don't forget to update the docs (follow `PEP257 <https://www.python.org/dev/peps/pep-0257/>`_).
3. Run the linter and tests:

   .. code-block:: bash

       python3 setup.py lint test

   Make sure that:

   - there are no lint errors,
   - all tests are passing,
   - the coverage is above 95%.

4. Push your work and create a pull request.


Other instructions
-------------------------------------------------------------------------------

- **Importing modules** is okay for modules from standard library. If you want to include
  third-party module, please consult it on GitHub before.
- `Please use regular expressions only as a last resort. <http://imgur.com/j3G9xyP>`_ When possible, use string manipulations,
  such as :code:`split()` and then list operations. It is more readable.
