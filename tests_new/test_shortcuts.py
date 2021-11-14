from unittest.mock import patch

import requests

import pycaching
from pycaching import Geocaching
from tests_new.conftest import PASSWORD, USERNAME


def test_login(betamax_session: requests.Session):
    real_init = Geocaching.__init__

    def fake_init(self_, unused_argument=None):
        real_init(self_, session=betamax_session)

    # patching with the fake init method above to insert our session into the Geocaching object for testing
    with patch.object(Geocaching, "__init__", new=fake_init):
        pycaching.login(USERNAME, PASSWORD)
