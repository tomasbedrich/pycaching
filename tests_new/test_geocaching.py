import contextlib
import json
import os
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
from typing import Union
from unittest.mock import patch

import pytest

from pycaching import Geocaching
from pycaching.errors import LoginFailedException, NotLoggedInException
from tests_new.conftest import PASSWORD, USERNAME


def test_unauthorized_request(geocaching):
    with pytest.raises(NotLoggedInException):
        geocaching._request("/")


def test_login(geocaching):
    geocaching.login(USERNAME, PASSWORD)
    assert geocaching._logged_in
    assert geocaching._logged_username == USERNAME


def test_login_bad_credentials(geocaching):
    with pytest.raises(LoginFailedException):
        geocaching.login("0", "0")
    assert geocaching._logged_username is None


def test_login_twice_with_valid_credentials(geocaching):
    geocaching.login(USERNAME, PASSWORD)
    geocaching.login(USERNAME, PASSWORD)
    assert geocaching._logged_in
    assert geocaching._logged_username == USERNAME


def test_logout_when_relogin_is_attempted_with_invalid_credentials(geocaching):
    with pytest.raises(LoginFailedException):
        geocaching.login("0", "0")
    assert geocaching._logged_username is None


@pytest.mark.parametrize(
    "side_effect", [FileNotFoundError, ValueError, KeyError, IOError, CalledProcessError(1, "error")]
)
def test_login_failed_because_of_load_credentials_failed(geocaching, side_effect):
    with patch.object(Geocaching, "_load_credentials", side_effect=side_effect):
        with pytest.raises(LoginFailedException):
            geocaching.login()


def test_get_logged_user(geocaching):
    geocaching.login(USERNAME, PASSWORD)
    assert geocaching.get_logged_user() == USERNAME


def test_logout(geocaching):
    geocaching.login(USERNAME, PASSWORD)
    geocaching.logout()
    assert not geocaching._logged_in
    assert geocaching._logged_username is None
    assert geocaching.get_logged_user() is None


class TestLoadCredentials:

    credentials = {"username": USERNAME, "password": PASSWORD}
    """A valid credentials file contents containing a single username/password combination."""

    multiuser_credentials = [
        {"username": USERNAME + "1", "password": PASSWORD + "1"},
        {"username": USERNAME + "2", "password": PASSWORD + "2"},
    ]
    """A valid credentials file contents containing multiple username/password combinations."""

    @staticmethod
    @contextlib.contextmanager
    def mock_credentials_file(geocaching: Geocaching, contents: Union[bytes, dict, list, str]):
        """Create a temporary credentials file with given contents and mock a Geocaching instance to use it."""
        backup = geocaching._credentials_file
        f = NamedTemporaryFile(delete=False)
        try:
            # bytes are written as-is, others are encoded to JSON
            if type(contents) is bytes:
                f.write(contents)
            else:
                f.write(json.dumps(contents).encode("utf-8"))
            f.flush()
            f.close()
            geocaching._credentials_file = f.name
            yield
        finally:
            os.remove(f.name)
            geocaching._credentials_file = backup

    def test(self, geocaching):
        with self.mock_credentials_file(geocaching, self.credentials):
            username, password = geocaching._load_credentials()
            assert USERNAME == username
            assert PASSWORD == password

    def test_with_username(self, geocaching):
        with self.mock_credentials_file(geocaching, self.credentials):
            username, password = geocaching._load_credentials(USERNAME)
            assert USERNAME == username
            assert PASSWORD == password

    def test_with_nonexisting_username(self, geocaching):
        with self.mock_credentials_file(geocaching, self.credentials):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials(USERNAME + "_nonexisting")

    def test_multiuser(self, geocaching):
        with self.mock_credentials_file(geocaching, self.multiuser_credentials):
            username, password = geocaching._load_credentials()
            assert USERNAME + "1" == username
            assert PASSWORD + "1" == password

    def test_multiuser_with_username(self, geocaching):
        with self.mock_credentials_file(geocaching, self.multiuser_credentials):
            username, password = geocaching._load_credentials(USERNAME + "2")
            assert USERNAME + "2" == username
            assert PASSWORD + "2" == password

    def test_multiuser_with_nonexisting_username(self, geocaching):
        with self.mock_credentials_file(geocaching, self.multiuser_credentials):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials(USERNAME + "3")

    def test_file_nonexisting(self, geocaching):
        geocaching._credentials_file = "this_file_doesnt_exist.json"
        with pytest.raises(FileNotFoundError):
            username, password = geocaching._load_credentials()

    def test_file_empty(self, geocaching):
        with self.mock_credentials_file(geocaching, {}):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials()

    def test_file_multiuser_empty(self, geocaching):
        with self.mock_credentials_file(geocaching, []):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials()

    def test_file_multiuser_empty_item(self, geocaching):
        with self.mock_credentials_file(geocaching, [{}]):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials()

    def test_file_string(self, geocaching):
        with self.mock_credentials_file(geocaching, "to-be-written-as-string-to-json"):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials()

    def test_file_invalid_json(self, geocaching):
        with self.mock_credentials_file(geocaching, b"ss{}ef"):
            with pytest.raises(ValueError):
                username, password = geocaching._load_credentials()

    def test_password_cmd(self, geocaching):
        with self.mock_credentials_file(geocaching, {"username": USERNAME, "password_cmd": "echo {}".format(PASSWORD)}):
            username, password = geocaching._load_credentials()
            assert USERNAME == username
            assert PASSWORD == password

    def test_password_cmd_invalid(self, geocaching):
        with self.mock_credentials_file(geocaching, {"username": USERNAME, "password_cmd": "exit 1"}):
            with pytest.raises(CalledProcessError):
                username, password = geocaching._load_credentials()

    def test_password_cmd_ambiguous(self, geocaching):
        with self.mock_credentials_file(
            geocaching, {"username": USERNAME, "password": PASSWORD, "password_cmd": "exit 1"}
        ):
            with pytest.raises(KeyError):
                username, password = geocaching._load_credentials()
