from betamax.cassette.cassette import Placeholder

CLASSIFIED_COOKIES = ('gspkauth',)


def sanitize_cookies(interaction, cassette):
    response = interaction.as_response()
    response_cookies = response.headers.get('Set-Cookie', None)
    request = response.request
    request_cookies = request.headers.get('Cookie', None)

    secret_values = []
    if request_cookies:
        secret_values += find_secret_values(request_cookies)
    if response_cookies:
        secret_values += find_secret_values(response_cookies)
    for val in secret_values:
        cassette.placeholders.append(
            Placeholder(placeholder='<AUTH COOKIE>', replace=val)
        )


def find_secret_values(cookies):
    found_values = []
    cookies = cookies.split('; ')
    for name in CLASSIFIED_COOKIES:
        identifier = '{}='.format(name)
        for c in cookies:
            if c.startswith(identifier):
                found_values.append(c[c.index('=') + 1:])

    return found_values
