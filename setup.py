#!/usr/bin/env python3

from pathlib import Path
from setuptools import setup
from setuptools.command.test import test as TestCommand
from setuptools import Command


# see http://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-python-setuptools-test-command
class NoseTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=["nosetests", "--with-coverage", "--cover-package=pycaching"])


class LintCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import flake8.main
        import sys
        sys.argv = []
        flake8.main.main()

with Path("./README.rst").open(encoding="utf-8") as f:
    long_description = f.read()

with Path("./requirements.txt").open(encoding="utf-8") as f:
    requirements = list(filter(None, (row.strip() for row in f)))

info = {
    "name":                "pycaching",
    "version":             "3.5.4",  # PEP 386
    "author":              "Tomas Bedrich",
    "author_email":        "ja@tbedrich.cz",
    "url":                 "https://github.com/tomasbedrich/pycaching",
    "packages":            ["pycaching"],
    "provides":            ["pycaching"],
    "license":             "GNU Lesser General Public License (LGPL) v3.0",
    "description":         "Geocaching.com site crawler. Provides tools for searching, fetching caches and geocoding.",
    "long_description":    long_description,
    "keywords":            ["geocaching", "crawler", "geocache", "cache", "search", "geocode", "travelbug"],
    "install_requires":    requirements,
    "setup_requires":      ["nose", "flake8<3.0.0", "coverage"],  # flake8 >= 3.0 has incompatible API
    "cmdclass":            {"test": NoseTestCommand, "lint": LintCommand},
}

if __name__ == "__main__":
    setup(**info)
