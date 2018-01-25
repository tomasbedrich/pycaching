import os
import sys

from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from requests import Session

if sys.version_info.major == 2:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

with Betamax.configure() as config:
    config.cassette_library_dir = os.path.join('test', 'cassettes')
    config.serialize_with = 'prettyjson'

    username = os.environ.get('pycaching_test_username') or 'USERNAMEPLACEHOLDER'
    password = os.environ.get('pycaching_test_password') or 'PASSWORDPLACEHOLDER'

    config.define_cassette_placeholder('<USERNAME>', quote_plus(username))
    config.define_cassette_placeholder('<PASSWORD>', quote_plus(password))

Betamax.register_serializer(PrettyJSONSerializer)
session = Session()
recorder = Betamax(session, default_cassette_options={'serialize_with': 'prettyjson'})
