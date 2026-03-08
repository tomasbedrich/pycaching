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
cookie = os.environ.get("PYCACHING_TEST_COOKIE")
auth_cookie_placeholder = "<AUTH COOKIE>"


cassette_dir = Path("test/cassettes")
cassette_dir.mkdir(exist_ok=True)

# Betamax config is global
config = Betamax.configure()
config.cassette_library_dir = str(cassette_dir)
config.define_cassette_placeholder("<USERNAME>", quote_plus(username))
config.define_cassette_placeholder("<PASSWORD>", quote_plus(password))
config.before_record(callback=sanitize_cookies)
Betamax.register_serializer(PrettyJSONSerializer)


def _cassette_will_record(cassette_name, *, record=None):
    if record in ("all", "new_episodes"):
        return True

    return not (cassette_dir / "{}.json".format(cassette_name)).exists()


def _refresh_recording_auth(geocaching):
    if not cookie and (username == "USERNAMEPLACEHOLDER" or password == "PASSWORDPLACEHOLDER"):
        return

    current_cookie = geocaching._session.cookies.get("gspkauth")
    if current_cookie and current_cookie != auth_cookie_placeholder:
        return

    if cookie:
        expected_username = None if username == "USERNAMEPLACEHOLDER" else username
        geocaching.login_with_cookie(cookie, username=expected_username)
    else:
        geocaching._logged_in = False
        geocaching._logged_username = None
        geocaching.login(username, password)


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
            if cookie:
                cls.gc.login_with_cookie(cookie)
            else:
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

        original_use_cassette = cls.recorder.use_cassette

        def use_cassette_with_fresh_auth(cassette_name, *args, **kwargs):
            # Setup cassettes can replace the live auth cookie with the scrubbed
            # placeholder value. Refresh auth before recording the next cassette.
            if _cassette_will_record(cassette_name, record=kwargs.get("record")):
                _refresh_recording_auth(cls.gc)
            return original_use_cassette(cassette_name, *args, **kwargs)

        cls.recorder.use_cassette = use_cassette_with_fresh_auth
