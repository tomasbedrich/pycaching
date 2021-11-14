import itertools
import unittest
from unittest.mock import patch

from geopy.distance import great_circle

from pycaching import Cache, Point, Rectangle
from pycaching.errors import PMOnlyException, TooManyRequestsError
from pycaching.geocaching import SortOrder

from . import LoggedInTest


class TestMethods(LoggedInTest):
    def test_my_finds(self):
        with self.recorder.use_cassette("geocaching_my_finds"):
            finds = list(self.gc.my_finds(3))
            for cache in finds:
                self.assertTrue(cache.name)
                self.assertTrue(isinstance(cache, Cache))

    def test_my_dnfs(self):
        with self.recorder.use_cassette("geocaching_my_dnfs"):
            dnfs = list(self.gc.my_dnfs(3))
            for cache in dnfs:
                self.assertTrue(cache.name)
                self.assertTrue(isinstance(cache, Cache))

    def test_search(self):
        with self.subTest("normal"):
            tolerance = 2
            expected = {"GC5VJ0P", "GC41FJC", "GC50AQ6", "GC167Y7", "GC7RR74", "GC167Y7"}
            with self.recorder.use_cassette("geocaching_search"):
                found = {cache.wp for cache in self.gc.search(Point(49.733867, 13.397091), 20)}
            self.assertGreater(len(expected & found), len(expected) - tolerance)

        with self.subTest("pagging"):
            with self.recorder.use_cassette("geocaching_search_pagination"):
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
            with self.recorder.use_cassette("geocaching_quick_normal"):
                # Once this feature is fixed, the corresponding cassette will have to be deleted
                # and re-recorded.
                res = [c.wp for c in self.gc.search_quick(rect)]
            for wp in ["GC41FJC", "GC17E8Y", "GC383XN"]:
                self.assertIn(wp, res)
            # but 108 caches larger tile
            self.assertLess(len(res), 130)
            self.assertGreater(len(res), 90)

        with self.subTest("strict handling of cache coordinates"):
            with self.recorder.use_cassette("geocaching_quick_strictness"):
                res = list(self.gc.search_quick(rect, strict=True))
            self.assertLess(len(res), expected_cache_num + tolerance)
            self.assertGreater(len(res), expected_cache_num - tolerance)

        with self.subTest("larger zoom - more precise"):
            with self.recorder.use_cassette("geocaching_quick_zoom"):
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
        with self.recorder.use_cassette("geocaching_matchload"):
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
        with self.recorder.use_cassette("geocaching__try_getting_cache_from_guid"):
            cache = self.gc._try_getting_cache_from_guid("15ad3a3d-92c1-4f7c-b273-60937bcc2072")
            self.assertEqual("Nekonecne ticho", cache.name)

    def test__try_getting_cache_from_guid_pm_only(self):
        # get PMonly cache from GC code (doesn't load any information)
        with self.recorder.use_cassette("geocaching__try_getting_cache_from_guid_pm_only"):
            try:
                cache_pm = self.gc._try_getting_cache_from_guid("328927c1-aa8c-4e0d-bf59-31f1ce44d990")
                cache_pm.load_quick()  # necessary to get name for PMonly cache
                self.assertEqual("Nidda: jenseits der Rennstrecke Reloaded", cache_pm.name)
            except PMOnlyException:
                pass


class TestAPIMethods(LoggedInTest):
    def test_search_rect(self):
        """Perform search by rect and check found caches."""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.39))

        expected = {"GC1TYYG", "GC11PRW", "GC7JRR5", "GC161KR", "GC1GW54", "GC7KDWE", "GC93HA6", "GCZC5D"}

        orig_wait_for = TooManyRequestsError.wait_for
        with self.recorder.use_cassette("geocaching_search_rect") as vcr:
            with patch.object(TooManyRequestsError, "wait_for", autospec=True) as wait_for:
                wait_for.side_effect = orig_wait_for if vcr.current_cassette.is_recording() else None

                with self.subTest("default use"):
                    caches = self.gc.search_rect(rect)
                    waypoints = {cache.wp for cache in caches}
                    self.assertSetEqual(waypoints, expected)

                with self.subTest("sort by distance"):
                    with self.assertRaises(AssertionError):
                        caches = list(self.gc.search_rect(rect, sort_by="distance"))

                    origin = Point.from_string("N 49° 44.230 E 013° 22.858")
                    caches = list(self.gc.search_rect(rect, sort_by=SortOrder.distance, origin=origin))
                    waypoints = {cache.wp for cache in caches}
                    self.assertSetEqual(waypoints, expected)

                    # Check if caches are sorted by distance to origin
                    distances = []
                    for cache in caches:
                        try:
                            distances.append(great_circle(cache.location, origin).meters)
                        except PMOnlyException:
                            # can happend when getting accurate location
                            continue
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

        with self.recorder.use_cassette("geocaching_api_rate_limit") as vcr:
            orig_wait_for = TooManyRequestsError.wait_for

            with patch.object(TooManyRequestsError, "wait_for", autospec=True) as wait_for:
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

        with self.recorder.use_cassette("geocaching_api_rate_limit_with_none") as vcr:
            with patch.object(TooManyRequestsError, "wait_for", autospec=True) as wait_for:
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


class TestShortcuts(LoggedInTest):
    def test_geocode(self):
        ref_point = Point(50.08746, 14.42125)
        with self.recorder.use_cassette("geocaching_shortcut_geocode"):
            self.assertLess(great_circle(self.gc.geocode("Prague"), ref_point).miles, 10)

    def test_get_cache(self):
        with self.recorder.use_cassette("geocaching_shortcut_getcache"):
            c = self.gc.get_cache("GC4808G")
            self.assertEqual("Nekonecne ticho", c.name)

    def test_get_cache_by_guid(self):
        with self.recorder.use_cassette("geocaching_shortcut_getcache_by_guid"):
            cache = self.gc.get_cache(guid="15ad3a3d-92c1-4f7c-b273-60937bcc2072")
            self.assertEqual("Nekonecne ticho", cache.name)

    def test_get_trackable(self):
        with self.recorder.use_cassette("geocaching_shortcut_gettrackable"):
            t = self.gc.get_trackable("TB1KEZ9")
            self.assertEqual("Lilagul #2: SwedenHawk Geocoin", t.name)

    def test_post_log(self):
        # I refuse to write 30 lines of tests (mocking etc.) because of 4 simple lines of code.
        pass
