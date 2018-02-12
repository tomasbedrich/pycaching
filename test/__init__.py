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

username = os.environ.get('PYCACHING_TEST_USERNAME') or 'USERNAMEPLACEHOLDER'
password = os.environ.get('PYCACHING_TEST_PASSWORD') or 'PASSWORDPLACEHOLDER'

path = str(Path('test/cassettes'))

with Betamax.configure() as config:
    config.cassette_library_dir = path
    config.define_cassette_placeholder('<USERNAME>', quote_plus(username))
    config.define_cassette_placeholder('<PASSWORD>', quote_plus(password))
    config.before_record(callback=sanitize_cookies)

Betamax.register_serializer(PrettyJSONSerializer)
session = Session()
recorder = Betamax(session, default_cassette_options={'serialize_with': 'prettyjson'})


class NetworkedTest(unittest.TestCase):
    """Class to represent tests that perform network requests"""

    @classmethod
    def setUpClass(cls):
        cls.gc = Geocaching(session=session)
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
            cls.gc._session = session  # it got redefined; fix it
