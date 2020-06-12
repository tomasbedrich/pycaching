#!/usr/bin/env python3

import itertools
import json
import os
import unittest
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from geopy.distance import great_circle

import pycaching
from pycaching import Cache, Geocaching, Point, Rectangle
from pycaching.errors import NotLoggedInException, LoginFailedException, PMOnlyException, TooManyRequestsError
from pycaching.geocaching import SortOrder
from . import username as _username, password as _password, NetworkedTest


class TestMethods(NetworkedTest):
    def test_my_finds(self):
        with self.recorder.use_cassette('geocaching_my_finds'):
            finds = list(self.gc.my_finds(20))
            self.assertEqual(20, len(finds))
            for cache in finds:
                self.assertTrue(cache.name)
                self.assertTrue(isinstance(cache, Cache))

    def test_my_dnfs(self):
        with self.recorder.use_cassette('geocaching_my_dnfs'):
            dnfs = list(self.gc.my_dnfs(20))
            self.assertEqual(20, len(dnfs))
            for cache in dnfs:
                self.assertTrue(cache.name)
                self.assertTrue(isinstance(cache, Cache))

    def test_search(self):
        with self.subTest("normal"):
            tolerance = 2
            expected = {"GC5VJ0P", "GC41FJC", "GC17E8Y", "GC14AV5", "GC50AQ6", "GC167Y7"}
            with self.recorder.use_cassette('geocaching_search'):
                found = {cache.wp for cache in self.gc.search(Point(49.733867, 13.397091), 20)}
            self.assertGreater(len(expected & found), len(expected) - tolerance)

        with self.subTest("pagging"):
            with self.recorder.use_cassette('geocaching_search_pagination'):
                caches = list(self.gc.search(Point(49.733867, 13.397091), 100))
            self.assertNotEqual(caches[0], caches[50])

    @unittest.expectedFailure
    def test_search_quick(self):
        """Perform quick search and check found caches"""
        # at time of writing, there were exactly 16 caches in this area + one PM only
        expected_cache_num = 16
        tolerance = 7
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.40))

        with self.subTest("normal"):
            with self.recorder.use_cassette('geocaching_quick_normal'):
                # Once this feature is fixed, the corresponding cassette will have to be deleted
                # and re-recorded.
                res = [c.wp for c in self.gc.search_quick(rect)]
            for wp in ["GC41FJC", "GC17E8Y", "GC383XN"]:
                self.assertIn(wp, res)
            # but 108 caches larger tile
            self.assertLess(len(res), 130)
            self.assertGreater(len(res), 90)

        with self.subTest("strict handling of cache coordinates"):
            with self.recorder.use_cassette('geocaching_quick_strictness'):
                res = list(self.gc.search_quick(rect, strict=True))
            self.assertLess(len(res), expected_cache_num + tolerance)
            self.assertGreater(len(res), expected_cache_num - tolerance)

        with self.subTest("larger zoom - more precise"):
            with self.recorder.use_cassette('geocaching_quick_zoom'):
                res1 = list(self.gc.search_quick(rect, strict=True, zoom=15))
                res2 = list(self.gc.search_quick(rect, strict=True, zoom=14))
            for res in res1, res2:
                self.assertLess(len(res), expected_cache_num + tolerance)
                self.assertGreater(len(res), expected_cache_num - tolerance)
            for c1, c2 in itertools.product(res1, res2):
                self.assertLess(c1.location.precision, c2.location.precision)

    @unittest.expectedFailure
    def test_search_quick_match_load(self):
        """Test if quick search results matches exact cache locations."""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.39))
        with self.recorder.use_cassette('geocaching_matchload'):
            # at commit time, this test is an allowed failure. Once this feature is fixed, the
            # corresponding cassette will have to be deleted and re-recorded.
            caches = list(self.gc.search_quick(rect, strict=True, zoom=15))
            for cache in caches:
                try:
                    cache.load()
                    self.assertIn(cache.location, rect)
                except PMOnlyException:
                    pass

    def test__try_getting_cache_from_guid(self):
        # get "normal" cache from guidpage
        with self.recorder.use_cassette('geocaching_shortcut_getcache__by_guid'):  # is a replacement for login
            cache = self.gc._try_getting_cache_from_guid('15ad3a3d-92c1-4f7c-b273-60937bcc2072')
            self.assertEqual("Nekonecne ticho", cache.name)

        # get PMonly cache from GC code (doesn't load any information)
        cache_pm = self.gc._try_getting_cache_from_guid('328927c1-aa8c-4e0d-bf59-31f1ce44d990')
        cache_pm.load_quick()  # necessary to get name for PMonly cache
        self.assertEqual("Nidda: jenseits der Rennstrecke Reloaded", cache_pm.name)


class TestAPIMethods(NetworkedTest):
    def test_search_rect(self):
        """Perform search by rect and check found caches."""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.39))

        expected = {'GC1TYYG', 'GC11PRW', 'GC7JRR5', 'GC161KR', 'GC1GW54', 'GC7KDWE', 'GC8D303'}

        orig_wait_for = TooManyRequestsError.wait_for
        with self.recorder.use_cassette('geocaching_search_rect') as vcr:
            with patch.object(TooManyRequestsError, 'wait_for', autospec=True) as wait_for:
                wait_for.side_effect = orig_wait_for if vcr.current_cassette.is_recording() else None
                with self.subTest("default use"):
                    caches = self.gc.search_rect(rect)
                    waypoints = {cache.wp for cache in caches}

                    self.assertSetEqual(waypoints, expected)

                with self.subTest("sort by distance"):
                    with self.assertRaises(AssertionError):
                        caches = list(self.gc.search_rect(rect, sort_by='distance'))

                    origin = Point.from_string('N 49° 44.230 E 013° 22.858')

                    caches = list(self.gc.search_rect(rect, sort_by=SortOrder.distance, origin=origin))

                    waypoints = [cache.wp for cache in caches]
                    self.assertEqual(waypoints,  [
                        'GC11PRW', 'GC1TYYG', 'GC7JRR5', 'GC1GW54', 'GC161KR', 'GC7KDWE', 'GC8D303'
                    ])

                    # Check if caches are sorted by distance to origin
                    distances = [great_circle(cache.location, origin).meters for cache in caches]
                    self.assertEqual(distances, sorted(distances))

                with self.subTest("sort by different criteria"):
                    for sort_by in SortOrder:
                        if sort_by is SortOrder.distance:
                            continue
                        caches = self.gc.search_rect(rect, sort_by=sort_by)
                        waypoints = {cache.wp for cache in caches}
                        self.assertSetEqual(waypoints, expected)

    def test_recover_from_rate_limit(self):
        """Test recovering from API rate limit exception."""
        rect = Rectangle(Point(50.74, 13.38), Point(49.73, 14.40))  # large rectangle

        with self.recorder.use_cassette('geocaching_api_rate_limit') as vcr:
            orig_wait_for = TooManyRequestsError.wait_for

            with patch.object(TooManyRequestsError, 'wait_for', autospec=True) as wait_for:
                # If we are recording, we must perform real wait, otherwise we skip waiting
                wait_for.side_effect = orig_wait_for if vcr.current_cassette.is_recording() else None

                for i, _cache in enumerate(self.gc.search_rect(rect, per_query=1)):
                    if wait_for.called:
                        self.assertEqual(wait_for.call_count, 1)
                        break

                    if i > 20:  # rate limit should be released after ~10 requests
                        self.fail("API Rate Limit not released")

    def test_recover_from_rate_limit_without_sleep(self):
        """Test recovering from API rate limit exception without sleep."""
        rect = Rectangle(Point(50.74, 13.38), Point(49.73, 14.40))

        with self.recorder.use_cassette('geocaching_api_rate_limit_with_none') as vcr:
            with patch.object(TooManyRequestsError, 'wait_for', autospec=True) as wait_for:
                caches = self.gc.search_rect(rect, per_query=1, wait_sleep=False)
                for i, cache in enumerate(caches):
                    if cache is None:
                        import time
                        while cache is None:
                            if vcr.current_cassette.is_recording():
                                time.sleep(10)
                            cache = next(caches)
                        self.assertIsInstance(cache, Cache)
                        break

                    if i > 20:
                        self.fail("API Rate Limit not released")

                self.assertEqual(wait_for.call_count, 0)


class TestLoginOperations(NetworkedTest):
    def setUp(self):
        super().setUp()
        self.gc = Geocaching(session=self.session)

    def test_request(self):
        with self.subTest("login needed"):
            with self.assertRaises(NotLoggedInException):
                self.gc._request("/")

    def test_login(self):
        with self.subTest("bad credentials"):
            with self.recorder.use_cassette('geocaching_badcreds'):
                self.session.cookies.clear()
                with self.assertRaises(LoginFailedException):
                    self.gc.login("0", "0")

        with self.subTest("good credentials twice"):
            self.gc.logout()
            self.session.cookies.clear()
            self.gc._session = self.session  # gotta reattach so we can keep listening
            with self.recorder.use_cassette('geocaching_2login'):
                self.gc.login(_username, _password)
                self.gc.login(_username, _password)

        with self.subTest("bad credentials automatic logout"):
            with self.recorder.use_cassette('geocaching_badcreds_logout'):
                self.gc.logout()
                self.session.cookies.clear()
                self.gc._session = self.session  # gotta reattach so we can keep listening
                with self.assertRaises(LoginFailedException):
                    self.gc.login("0", "0")

        with self.subTest("FileNotFoundError is reraised as LoginFailedException"):
            with patch.object(Geocaching, "_load_credentials",
                              side_effect=FileNotFoundError):
                with self.assertRaises(LoginFailedException):
                    self.gc.login()

        with self.subTest("ValueError is reraised as LoginFailedException"):
            with patch.object(Geocaching, "_load_credentials",
                              side_effect=ValueError):
                with self.assertRaises(LoginFailedException):
                    self.gc.login()

        with self.subTest("KeyError is reraised as LoginFailedException"):
            with patch.object(Geocaching, "_load_credentials",
                              side_effect=KeyError):
                with self.assertRaises(LoginFailedException):
                    self.gc.login()

        with self.subTest("IOError is reraised as LoginFailedException"):
            with patch.object(Geocaching, "_load_credentials",
                              side_effect=IOError):
                with self.assertRaises(LoginFailedException):
                    self.gc.login()

        with self.subTest("CalledProcessError is reraised as LoginFailedException"):
            with patch.object(Geocaching, "_load_credentials",
                              side_effect=CalledProcessError(1, "error")):
                with self.assertRaises(LoginFailedException):
                    self.gc.login()

    def test_get_logged_user(self):
        with self.recorder.use_cassette('geocaching_loggeduser'):
            self.gc.login(_username, _password)
            self.assertEqual(self.gc.get_logged_user(), _username)

    def test_logout(self):
        with self.recorder.use_cassette('geocaching_logout'):
            self.gc.login(_username, _password)
            self.gc.logout()
            self.session.cookies.clear()
            self.gc._session = self.session  # gotta reattach so we can keep listening
            self.assertIsNone(self.gc.get_logged_user())

    def test_load_credentials(self):
        filename_backup = self.gc._credentials_file
        credentials = {"username": _username, "password": _password}
        multi_credentials = [{"username": _username+"1", "password": _password+"1"},
                             {"username": _username+"2", "password": _password+"2"}]
        empty_valid_json = {}
        nonsense_str = b"ss{}ef"
        password_cmd = "echo {}".format(_password)
        invalid_cmd = "exit 1"

        with self.subTest("Try to load nonexistent file from current directory"):
            self.gc._credentials_file = "this_file_doesnt_exist.json"
            with self.assertRaises(FileNotFoundError):
                username, password = self.gc._load_credentials()

        # each of the following subtests consists of:
        # 1. creating tempfile with some contents and **closing it**
        # 3. doing some tests (will reopen tempfile)
        # 4. removing tempfile (whether the subtest passed or not)

        with self.subTest("Try to load valid credentials from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(credentials).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                username, password = self.gc._load_credentials()
                self.assertEqual(_username, username)
                self.assertEqual(_password, password)
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load valid credentials with username from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(credentials).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                username, password = self.gc._load_credentials(_username)
                self.assertEqual(_username, username)
                self.assertEqual(_password, password)
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load valid credentials with not existing username from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(credentials).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                with self.assertRaises(KeyError):
                    username, password = self.gc._load_credentials(_username+"3")
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load valid multi credentials with default user from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(multi_credentials).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                username, password = self.gc._load_credentials()
                self.assertEqual(_username+"1", username)
                self.assertEqual(_password+"1", password)
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load valid multi credentials with user from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(multi_credentials).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                username, password = self.gc._load_credentials(_username+"2")
                self.assertEqual(_username+"2", username)
                self.assertEqual(_password+"2", password)
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load valid multi credentials with not existing user from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(multi_credentials).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                with self.assertRaises(KeyError):
                    username, password = self.gc._load_credentials(_username+"3")
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load empty file from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as empty:
                    empty.write(json.dumps(empty_valid_json).encode())
                self.gc._credentials_file = os.path.basename(empty.name)
                with self.assertRaises(KeyError):
                    self.gc._load_credentials()
            finally:
                os.remove(empty.name)

        with self.subTest("Try to load very empty multi credential file from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps([]).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                with self.assertRaises(KeyError):
                    username, password = self.gc._load_credentials()
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load empty multi credential file from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps([empty_valid_json]).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                with self.assertRaises(KeyError):
                    username, password = self.gc._load_credentials()
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load multi credential file with invalid format from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps("username").encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                with self.assertRaises(KeyError):
                    username, password = self.gc._load_credentials()
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load nonsense file from current directory"):
            try:
                with NamedTemporaryFile(dir=".", delete=False) as nonsense:
                    nonsense.write(nonsense_str)
                self.gc._credentials_file = os.path.basename(nonsense.name)
                with self.assertRaises(ValueError):
                    self.gc._load_credentials()
            finally:
                os.remove(nonsense.name)

        with self.subTest("Try to load valid credentials from home directory"):
            try:
                with NamedTemporaryFile(dir=os.path.expanduser("~"), delete=False) as home_file:
                    home_file.write(json.dumps(credentials).encode())
                self.gc._credentials_file = os.path.basename(home_file.name)
                username, password = self.gc._load_credentials()
                self.assertEqual(_username, username)
                self.assertEqual(_password, password)
            finally:
                os.remove(home_file.name)

        with self.subTest("Try to load credentials with password cmd"):
            credentials_with_pass_cmd = {
                "username": _username, "password_cmd": password_cmd}
            try:
                with NamedTemporaryFile(dir=".", delete=False) as valid:
                    valid.write(json.dumps(credentials_with_pass_cmd).encode())
                self.gc._credentials_file = os.path.basename(valid.name)
                username, password = self.gc._load_credentials()
                self.assertEqual(_username, username)
                self.assertEqual(_password, password)
            finally:
                os.remove(valid.name)

        with self.subTest("Try to load credentials with invalid password cmd"):
            credentials_with_pass_cmd = {
                "username": _username, "password_cmd": invalid_cmd}
            try:
                with NamedTemporaryFile(dir=".", delete=False) as invalid:
                    invalid.write(json.dumps(credentials_with_pass_cmd).encode())
                self.gc._credentials_file = os.path.basename(invalid.name)
                with self.assertRaises(CalledProcessError):
                    self.gc._load_credentials()
            finally:
                os.remove(invalid.name)

        with self.subTest("Try to load credentials with ambiguous password"):
            credentials_with_ambiguous_pass = {"username": _username,
                                               "password": _password,
                                               "password_cmd": password_cmd}
            try:
                with NamedTemporaryFile(dir=".", delete=False) as ambiguous:
                    ambiguous.write(json.dumps(credentials_with_ambiguous_pass).encode())
                self.gc._credentials_file = os.path.basename(ambiguous.name)
                with self.assertRaises(KeyError):
                    self.gc._load_credentials()
            finally:
                os.remove(ambiguous.name)

        self.gc._credentials_file = filename_backup


class TestShortcuts(NetworkedTest):
    def test_login(self):
        real_init = Geocaching.__init__

        def fake_init(self_, unused_argument=None):
            real_init(self_, session=self.session)

        # patching with the fake init method above to insert our session into the Geocaching object for testing
        with patch.object(Geocaching, '__init__', new=fake_init):
            with self.recorder.use_cassette('geocaching_shortcut_login'):
                pycaching.login(_username, _password)

    def test_geocode(self):
        ref_point = Point(50.08746, 14.42125)
        with self.recorder.use_cassette('geocaching_shortcut_geocode'):
            self.assertLess(great_circle(self.gc.geocode("Prague"), ref_point).miles, 10)

    def test_get_cache(self):
        with self.recorder.use_cassette('geocaching_shortcut_getcache'):
            c = self.gc.get_cache("GC4808G")
            self.assertEqual("Nekonecne ticho", c.name)

    def test_get_cache__by_guid(self):
        with self.recorder.use_cassette('geocaching_shortcut_getcache__by_guid'):
            cache = self.gc.get_cache(guid='15ad3a3d-92c1-4f7c-b273-60937bcc2072')
            self.assertEqual("Nekonecne ticho", cache.name)

    def test_get_trackable(self):
        with self.recorder.use_cassette('geocaching_shortcut_gettrackable'):
            t = self.gc.get_trackable("TB1KEZ9")
            self.assertEqual("Lilagul #2: SwedenHawk Geocoin", t.name)

    def test_post_log(self):
        # I refuse to write 30 lines of tests (mocking etc.) because of 4 simple lines of code.
        pass
