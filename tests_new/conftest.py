import os
from pathlib import Path
from urllib.parse import quote_plus

import pytest
import requests
from betamax import Betamax
from betamax.cassette.cassette import Placeholder
from betamax_serializers.pretty_json import PrettyJSONSerializer

from pycaching.geocaching import Geocaching

USERNAME = os.environ.get("PYCACHING_TEST_USERNAME") or "USERNAMEPLACEHOLDER"
PASSWORD = os.environ.get("PYCACHING_TEST_PASSWORD") or "PASSWORDPLACEHOLDER"
CLASSIFIED_COOKIES = (
    "gspkauth",
    "__RequestVerificationToken",
    "jwt",  # NOTE: JWT token, contains user related informations: username, ids, oauth token
)
CASSETTE_DIR = Path(__file__).parent / "cassettes"


@pytest.fixture(scope="session", autouse=True)
def betamax_config():
    CASSETTE_DIR.mkdir(exist_ok=True)
    Betamax.register_serializer(PrettyJSONSerializer)
    _betamax_config = Betamax.configure()
    _betamax_config.cassette_library_dir = str(CASSETTE_DIR)
    _betamax_config.define_cassette_placeholder("<USERNAME>", quote_plus(USERNAME))
    _betamax_config.define_cassette_placeholder("<PASSWORD>", quote_plus(PASSWORD))
    _betamax_config.before_record(callback=_sanitize_betamax_cookies)
    _betamax_config.default_cassette_options["serialize_with"] = "prettyjson"


@pytest.fixture(autouse=True)
def betamax_forgotten_recording_env_vars_fuse(betamax_recorder: Betamax):
    """Prevent recording failing set of cassettess."""
    if betamax_recorder.current_cassette.is_recording() and USERNAME == "USERNAMEPLACEHOLDER":
        pytest.exit(
            "You tried to record a cassette without providing Geocaching credentials. "
            "Please provide PYCACHING_TEST_USERNAME and PYCACHING_TEST_PASSWORD to record new cassettes.",
            returncode=1,
        )


@pytest.fixture
def geocaching(betamax_session: requests.Session):
    return Geocaching(session=betamax_session)


@pytest.fixture
def geocaching_logged_in(betamax_session: requests.Session):
    gc = Geocaching(session=betamax_session)
    gc.login(USERNAME, PASSWORD)
    return gc


def _sanitize_betamax_cookies(interaction, cassette):
    # TODO handle also request body occurence of __RequestVerificationToken
    response = interaction.as_response()
    response_cookies = response.cookies
    request_cookies = dict()
    for cookie in (interaction.as_response().request.headers.get("Cookie") or "").split("; "):
        name, sep, val = cookie.partition("=")
        if sep:
            request_cookies[name] = val

    secret_values = set()
    for name in CLASSIFIED_COOKIES:
        potential_val = response_cookies.get(name)
        if potential_val:
            secret_values.add(potential_val)

        potential_val = request_cookies.get(name)
        if potential_val:
            secret_values.add(potential_val)

    for val in secret_values:
        cassette.placeholders.append(Placeholder(placeholder="<AUTH COOKIE>", replace=val))
