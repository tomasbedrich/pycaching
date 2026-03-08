import json
import secrets
from test.cassette_sanitizer import sanitize_betamax_interaction
from types import SimpleNamespace
from uuid import uuid4

import pytest
import requests


@pytest.fixture(autouse=True)
def betamax_forgotten_recording_env_vars_fuse():
    """Override the autouse fuse; this unit test does not record network traffic."""


def test_sanitize_betamax_interaction_collects_requested_placeholders():
    auth_cookie = secrets.token_urlsafe(16)
    rotated_auth_cookie = secrets.token_urlsafe(16)
    request_token = secrets.token_urlsafe(18)
    response_token = secrets.token_urlsafe(20)
    viewstate = secrets.token_urlsafe(24)
    viewstate_generator = secrets.token_hex(4).upper()
    username = "user_" + secrets.token_hex(4)
    user_guid = str(uuid4())
    user_id = str(secrets.randbelow(90_000_000) + 10_000_000)
    user_code = "PR" + secrets.token_hex(3).upper()
    user_token = secrets.token_urlsafe(40)
    user_created_date = "2011-11-11T11:11:11"
    membership_level = "1"
    locale = "en-US"
    date_format = "dd.MM.yyyy"
    home_coords = "12.123456,12.123456"
    client_ip_coordinate = json.dumps({"latitude": 12.123456, "longitude": 12.123456})
    next_data = json.dumps(
        {
            "props": {
                "pageProps": {
                    "gcUser": {
                        "id": int(user_id),
                        "username": username,
                        "publicGuid": user_guid,
                        "referenceCode": user_code,
                        "dateCreated": user_created_date,
                        "locale": locale,
                        "membershipLevel": int(membership_level),
                        "dateFormat": date_format,
                        "clientIpCoordinate": json.loads(client_ip_coordinate),
                    }
                }
            }
        }
    )

    interaction = SimpleNamespace(
        data={
            "request": {
                "uri": "https://www.geocaching.com/seek/geocache.logbook?tkn=TOKEN",
                "headers": {
                    "Cookie": ["gspkauth={}; __RequestVerificationToken={}".format(auth_cookie, request_token)],
                },
                "body": {
                    "string": "__RequestVerificationToken={}&__VIEWSTATE={}".format(request_token, viewstate),
                },
            },
            "response": {
                "url": "https://www.geocaching.com/cache?saddr={}".format(home_coords),
                "headers": {
                    "Set-Cookie": [
                        "gspkauth={}; path=/; secure; HttpOnly".format(rotated_auth_cookie),
                    ],
                },
                "body": {
                    "string": """
                    <input type="hidden" name="__VIEWSTATEGENERATOR" value="{viewstate_generator}" />
                    <input type="hidden" name="__RequestVerificationToken" value="{response_token}" />
                     <script>
                     window['chromeSettings'] = {{"accountId": {user_id}, "username": "{username}",
                     "userPublicGuid": "{user_guid}",
                     "referenceCode": "{user_code}", "homeCoords": "{home_coords}"}};
                     window['userRef'] = '{user_code}';
                     userToken = '{user_token}';
                     </script>
                     <script id="__NEXT_DATA__" type="application/json">
                     {next_data}
                     </script>
                     """.format(
                        response_token=response_token,
                        viewstate_generator=viewstate_generator,
                        user_id=user_id,
                        username=username,
                        user_guid=user_guid,
                        user_code=user_code,
                        user_token=user_token,
                        home_coords=home_coords,
                        next_data=next_data,
                    ),
                },
            },
        }
    )

    response = SimpleNamespace(
        cookies=requests.cookies.cookiejar_from_dict(
            {"gspkauth": auth_cookie, "__RequestVerificationToken": response_token}
        ),
        request=SimpleNamespace(
            headers={"Cookie": "gspkauth={}; __RequestVerificationToken={}".format(auth_cookie, request_token)}
        ),
    )
    interaction.as_response = lambda: response

    cassette = SimpleNamespace(placeholders=[])

    sanitize_betamax_interaction(interaction, cassette)

    placeholders = {(item.placeholder, item.replace) for item in cassette.placeholders}
    chrome_settings_values = [value for placeholder, value in placeholders if placeholder == "<CHROME SETTINGS>"]
    assert len(chrome_settings_values) == 1
    assert user_id in chrome_settings_values[0]
    assert username in chrome_settings_values[0]
    assert user_guid in chrome_settings_values[0]
    assert user_code in chrome_settings_values[0]
    assert home_coords in chrome_settings_values[0]
    assert ("<AUTH COOKIE>", auth_cookie) in placeholders
    assert ("<AUTH COOKIE>", rotated_auth_cookie) in placeholders
    assert ("<AUTH COOKIE>", request_token) in placeholders
    assert ("<AUTH COOKIE>", response_token) in placeholders
    assert ("<VIEWSTATE>", viewstate) in placeholders
    assert ("<VIEWSTATEGENERATOR>", viewstate_generator) in placeholders
    assert ("<USERNAME>", username) in placeholders
    assert ("<USER GUID>", user_guid) in placeholders
    assert ("<USER ID>", user_id) in placeholders
    assert ("<USER CODE>", user_code) in placeholders
    assert ("<USER TOKEN>", user_token) in placeholders
    assert ("<USER CREATED DATE>", user_created_date) in placeholders
    assert ("<CLIENT IP COORDINATE>", client_ip_coordinate) in placeholders
    assert ("<HOME COORDS>", home_coords) in placeholders
