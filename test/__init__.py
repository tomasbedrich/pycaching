import os
import pathlib
from urllib.parse import quote_plus

from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from requests import Session

from .helpers import sanitize_cookies

username = os.environ.get('PYCACHING_TEST_USERNAME') or 'USERNAMEPLACEHOLDER'
password = os.environ.get('PYCACHING_TEST_PASSWORD') or 'PASSWORDPLACEHOLDER'

path = pathlib.Path('test', 'cassettes')

with Betamax.configure() as config:
    config.cassette_library_dir = str(path)
    config.define_cassette_placeholder('<USERNAME>', quote_plus(username))
    config.define_cassette_placeholder('<PASSWORD>', quote_plus(password))
    config.before_record(callback=sanitize_cookies)

Betamax.register_serializer(PrettyJSONSerializer)
session = Session()
recorder = Betamax(session, default_cassette_options={'serialize_with': 'prettyjson'})
