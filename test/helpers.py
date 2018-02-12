from betamax.cassette.cassette import Placeholder

CLASSIFIED_COOKIES = ('gspkauth', '__RequestVerificationToken')


def sanitize_cookies(interaction, cassette):
    response = interaction.as_response()
    response_cookies = response.cookies
    request_body = response.request.body or ''  # where secret values hide
    # the or '' is necessary above because sometimes response.request.body
    # is empty bytes, and that makes the later code complain.

    secret_values = set()
    for name in CLASSIFIED_COOKIES:
        potential_val = response_cookies.get(name)
        if potential_val:
            secret_values.add(potential_val)

        named_parameter_str = '&{}='.format(name)
        if (named_parameter_str in request_body
            or request_body.startswith(named_parameter_str[1:])):
            i = request_body.index(name) + len(name) + 1  # +1 for the = sign
            val = request_body[i:].split(',')[0]  # after the comma is another cookie
            secret_values.add(val)

    for val in secret_values:
        cassette.placeholders.append(
            Placeholder(placeholder='<AUTH COOKIE>', replace=val)
        )
