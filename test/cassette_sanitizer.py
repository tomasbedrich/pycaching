"""Shared Betamax cassette sanitization helpers for recorded fixtures.

The suite records authenticated traffic, so cassettes may capture user-specific
values that are irrelevant to assertions: auth tokens, page bootstrap user
metadata, ASP.NET hidden fields, and home-location coordinates in URLs.
This module keeps the scrubbing rules in one place for both unittest and
pytest-based Betamax setups.
"""

import re

from betamax.cassette.cassette import Placeholder

CLASSIFIED_COOKIES = (
    "gspkauth",
    "__RequestVerificationToken",
    "jwt",
)

# Each rule must contain exactly one capture group with the sensitive value.
# Variables are exported for use in tests that assert on placeholder values.
PLACEHOLDER_RULES = {
    # This bootstrap object is not parsed by library code, so replacing its
    # contents wholesale keeps fixtures smaller and hides a lot of account data.
    "<CHROME SETTINGS>": (re.compile(r"window\['chromeSettings'\]\s*=\s*\{([\s\S]*?)\};"),),
    "<AUTH COOKIE>": (
        re.compile(r"__RequestVerificationToken=([^&\"\s]+)"),
        re.compile(r'"__RequestVerificationToken"\s*:\s*"([^"]+)"'),
        re.compile(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"'),
    ),
    "<VIEWSTATE>": (
        re.compile(r'name="__VIEWSTATE"[^>]*value="([^"]+)"'),
        re.compile(r"__VIEWSTATE=([^&\"\s]+)"),
    ),
    "<VIEWSTATE1>": (
        re.compile(r'name="__VIEWSTATE1"[^>]*value="([^"]+)"'),
        re.compile(r"__VIEWSTATE1=([^&\"\s]+)"),
    ),
    "<VIEWSTATEGENERATOR>": (
        re.compile(r'name="__VIEWSTATEGENERATOR"[^>]*value="([^"]+)"'),
        re.compile(r"__VIEWSTATEGENERATOR=([^&\"\s]+)"),
    ),
    "<USERNAME>": (
        re.compile(r'"username"\s*:\s*"([^"]+)"'),
        re.compile(r'"Username"\s*:\s*"([^"]+)"'),
    ),
    "<USER GUID>": (re.compile(r'"(?:publicGuid|PublicGuid|userPublicGuid)"\s*:\s*"([^"]+)"'),),
    "<USER ID>": (
        re.compile(r'"accountId"\s*:\s*(\d+)'),
        re.compile(r'"gcUser"\s*:\s*\{[\s\S]*?"id"\s*:\s*(\d+)'),
    ),
    "<USER CODE>": (
        re.compile(r'"referenceCode"\s*:\s*"(P[A-Z0-9]+)"'),
        re.compile(r"window\['userRef'\]\s*=\s*'([^']+)'"),
        re.compile(r'"userRef"\s*:\s*"([^"]+)"'),
    ),
    "<USER TOKEN>": (
        re.compile(r"\buserToken\s*=\s*'([^']+)'"),
        re.compile(r'"userToken"\s*:\s*"([^"]+)"'),
        re.compile(r"([?&]tkn=)([^&\"\s]+)"),
    ),
    "<HOME LOCATION>": (re.compile(r'"(?:homeLocation|HomeLocation)"\s*:\s*"([^"]+)"'),),
    "<HOME COORDS>": (
        re.compile(r'"(?:homeCoords|HomeCoords)"\s*:\s*"([^"]+)"'),
        re.compile(r"(?:[?&;]saddr=)(-?\d+(?:\.\d+)?(?:%2C|,)-?\d+(?:\.\d+)?)"),
    ),
    "<USER CREATED DATE>": (re.compile(r'"dateCreated"\s*:\s*"([^"]+)"'),),
    "<CLIENT IP COORDINATE>": (re.compile(r'"clientIpCoordinate"\s*:\s*(\{[^}]+\})'),),
}


def sanitize_betamax_interaction(interaction, cassette):
    """Register placeholders for sensitive values found in one Betamax interaction."""
    _collect_cookie_placeholders(interaction, cassette)

    for text in _iter_interaction_texts(interaction):
        for placeholder, patterns in PLACEHOLDER_RULES.items():
            for pattern in patterns:
                for value in pattern.findall(text):
                    if isinstance(value, tuple):
                        value = value[-1]
                    _add_placeholder(cassette, placeholder, value)


def _collect_cookie_placeholders(interaction, cassette):
    response = interaction.as_response()
    response_cookies = response.cookies
    request_cookies = {}
    response_headers = interaction.data.get("response", {}).get("headers", {})
    response_set_cookies = response_headers.get("Set-Cookie", [])

    for cookie in (response.request.headers.get("Cookie") or "").split("; "):
        name, sep, value = cookie.partition("=")
        if sep:
            request_cookies[name] = value

    for name in CLASSIFIED_COOKIES:
        _add_placeholder(cassette, "<AUTH COOKIE>", response_cookies.get(name))
        _add_placeholder(cassette, "<AUTH COOKIE>", request_cookies.get(name))
        for header in response_set_cookies:
            match = re.search(rf"(?:^|[;,]\s*){re.escape(name)}=([^;,\s]+)", header)
            if match:
                _add_placeholder(cassette, "<AUTH COOKIE>", match.group(1))


def _iter_interaction_texts(interaction):
    for obj, key in (("request", "uri"), ("response", "url")):
        value = interaction.data.get(obj, {}).get(key)
        if value:
            yield value

    for obj in ("request", "response"):
        headers = interaction.data.get(obj, {}).get("headers", {})
        for value in headers.values():
            if isinstance(value, list):
                yield "\n".join(value)
            elif value:
                yield value

        body = interaction.data.get(obj, {}).get("body", "")
        value = body.get("string") if isinstance(body, dict) else body
        if value:
            yield value


def _add_placeholder(cassette, placeholder, value):
    if not value or value.startswith("<"):
        return

    if any(item.placeholder == placeholder and item.replace == value for item in cassette.placeholders):
        return

    cassette.placeholders.append(Placeholder(placeholder=placeholder, replace=value))
