from betamax.cassette.cassette import Placeholder

CLASSIFIED_COOKIES = (
    "gspkauth",
    "__RequestVerificationToken",
    "jwt",  # NOTE: JWT token, contains user related informations: username, ids, oauth token
)


def sanitize_cookies(interaction, cassette):
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
