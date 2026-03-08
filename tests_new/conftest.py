import os
from pathlib import Path
from test.cassette_sanitizer import sanitize_betamax_interaction
from urllib.parse import quote_plus

import pytest
import requests
from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer

from pycaching.geocaching import Geocaching

USERNAME = os.environ.get("PYCACHING_TEST_USERNAME") or "USERNAMEPLACEHOLDER"
PASSWORD = os.environ.get("PYCACHING_TEST_PASSWORD") or "PASSWORDPLACEHOLDER"
COOKIE = os.environ.get("PYCACHING_TEST_COOKIE")
CASSETTE_DIR = Path(__file__).parent / "cassettes"


@pytest.fixture(scope="session", autouse=True)
def betamax_config():
    CASSETTE_DIR.mkdir(exist_ok=True)
    Betamax.register_serializer(PrettyJSONSerializer)
    _betamax_config = Betamax.configure()
    _betamax_config.cassette_library_dir = str(CASSETTE_DIR)
    _betamax_config.define_cassette_placeholder("<USERNAME>", quote_plus(USERNAME))
    _betamax_config.define_cassette_placeholder("<PASSWORD>", quote_plus(PASSWORD))
    _betamax_config.before_record(callback=sanitize_betamax_interaction)
    _betamax_config.default_cassette_options["serialize_with"] = "prettyjson"


@pytest.fixture(autouse=True)
def betamax_forgotten_recording_env_vars_fuse(betamax_recorder: Betamax):
    """Prevent recording failing set of cassettess."""
    if betamax_recorder.current_cassette.is_recording() and USERNAME == "USERNAMEPLACEHOLDER" and not COOKIE:
        pytest.exit(
            "You tried to record a cassette without providing authentication. "
            "Please provide PYCACHING_TEST_USERNAME and PYCACHING_TEST_PASSWORD, "
            "or provide PYCACHING_TEST_COOKIE to record new cassettes.",
            returncode=1,
        )


@pytest.fixture
def geocaching(betamax_session: requests.Session):
    return Geocaching(session=betamax_session)


@pytest.fixture
def geocaching_logged_in(betamax_session: requests.Session):
    gc = Geocaching(session=betamax_session)
    if COOKIE:
        gc.login_with_cookie(COOKIE)
    else:
        gc.login(USERNAME, PASSWORD)
    return gc
