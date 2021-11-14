import os
import unittest
from pathlib import Path
from urllib.parse import quote_plus

from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from requests import Session

from pycaching.errors import Error
from pycaching.geocaching import Geocaching

from .helpers import sanitize_cookies

username = os.environ.get("PYCACHING_TEST_USERNAME") or "USERNAMEPLACEHOLDER"
password = os.environ.get("PYCACHING_TEST_PASSWORD") or "PASSWORDPLACEHOLDER"


cassette_dir = Path("test/cassettes")
cassette_dir.mkdir(exist_ok=True)

# Betamax config is global
config = Betamax.configure()
config.cassette_library_dir = str(cassette_dir)
config.define_cassette_placeholder("<USERNAME>", quote_plus(username))
config.define_cassette_placeholder("<PASSWORD>", quote_plus(password))
config.before_record(callback=sanitize_cookies)
Betamax.register_serializer(PrettyJSONSerializer)


class NetworkedTest(unittest.TestCase):
    """Class to represent tests that perform network requests."""

    @classmethod
    def setUpClass(cls):
        cls.session = Session()
        cls.recorder = Betamax(cls.session, default_cassette_options={"serialize_with": "prettyjson"})
        cls.gc = Geocaching(session=cls.session)


class LoggedInTest(NetworkedTest):
    """Class to represent tests that work as logged-in to geocaching.com."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            cls.gc.login(username, password)
        except Error:
            # LoginFailedException is raised with invalid creds; Error is raised
            # with no network connection. This is okay as long as we aren't
            # recording new cassettes. If we are recording new cassettes, they
            # will indeed fail. But we shouldn't record and replay setup login,
            # because if we are recording new cassettes this means we cannot get
            # properly logged in.
            cls.gc._logged_in = True  # we're gonna trick it
            cls.gc._logged_username = username  # we're gonna trick it
            cls.gc._session = cls.session  # it got redefined; fix it
