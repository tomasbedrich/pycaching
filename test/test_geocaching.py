import datetime
from unittest import TestCase
from unittest.mock import call, patch

from bs4 import BeautifulSoup
from geopy.distance import great_circle

from pycaching import Cache, Geocaching, Point, Rectangle
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
            expected = {
                "GC50AQ6",
                "GC9T8WJ",
                "GC8Z14D",
                "GC167Y7",
                "GC7TT7T",
                "GC3TF1K",
                "GC77PV1",
                "GC84801",
                "GC5MGHV",
                "GC5VJ0P",
                "GC9PN94",
                "GC161KR",
                "GC7GNTE",
                "GC1M7GP",
                "GC5EDMF",
                "GC868VY",
                "GC44001",
                "GC3P972",
                "GC86RK3",
                "GC9TRPD",
            }
            with self.recorder.use_cassette("geocaching_search"):
                found = {cache.wp for cache in self.gc.search(Point(49.733867, 13.397091), 20)}
            self.assertGreater(len(expected & found), len(expected) - tolerance)

        with self.subTest("pagination"):
            with self.recorder.use_cassette("geocaching_search_pagination"):
                caches = list(self.gc.search(Point(49.733867, 13.397091), 100, per_query=50))
            self.assertNotEqual(caches[0], caches[50])

        with self.subTest("sort_str"):
            with self.recorder.use_cassette("geocaching_search"):
                caches = list(self.gc.search(Point(49.733867, 13.397091), 20, sort_by="datelastvisited"))
            self.assertGreater(len(expected & found), len(expected) - tolerance)

        with self.subTest("sort"):
            with self.recorder.use_cassette("geocaching_search"):
                caches = list(self.gc.search(Point(49.733867, 13.397091), 20, sort_by=SortOrder.date_last_visited))
            self.assertGreater(len(expected & found), len(expected) - tolerance)

    def test_search_quick(self):
        """Perform quick search and check found caches"""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.40))

        with self.recorder.use_cassette("geocaching_quick_search"):
            res = [c.wp for c in self.gc.search_quick(rect)]
        for wp in ["GC11PRW", "GC161KR", "GC167Y7"]:
            self.assertIn(wp, res)
        self.assertEqual(len(res), 11)

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


class TestMyLogs(TestCase):
    @staticmethod
    def _generate_page_soup(first, count=20, has_next=True):
        rows = "".join(
            (
                "<tr><td></td><td></td><td> 2026-10-15 </td>"
                '<td><a class="ImageLink" href="https://www.geocaching.com/geocache/GC{:X}"></a></td></tr>'.format(i)
            )
            for i in range(first, first + count)
        )
        next_link = (
            "<a href=\"javascript:__doPostBack('ctl00$ContentBody$pgrTop$ctl08','')\"><b>Next &gt;</b></a>"
            if has_next
            else '<a class="aspNetDisabled"><b>Next &gt;</b></a>'
        )
        return BeautifulSoup(
            (
                '<form id="aspnetForm"><input type="hidden" name="__EVENTTARGET" value="" />'
                '<input type="hidden" name="__EVENTARGUMENT" value="" />'
                '<input type="hidden" name="__VIEWSTATE" value="state-{}" />'
                '<input type="hidden" name="__VIEWSTATEGENERATOR" value="85D312FD" />'
                '<table class="Table"><tbody>{}</tbody></table>{}</form>'
                '<form id="form-logout"><input type="hidden" name="returnUrl" /></form>'.format(first, rows, next_link)
            ),
            "html.parser",
        )

    def test_pagination(self):
        gc = Geocaching()
        for method, kwargs, url in [
            (gc.my_finds, {}, "my/logs.aspx?lt=2"),
            (gc.my_dnfs, {}, "my/logs.aspx?lt=3"),
            (gc.my_logs, {}, "my/logs.aspx"),
            (gc.my_logs, {"log_type": "2"}, "my/logs.aspx?lt=2"),
        ]:
            with self.subTest(method=method.__name__, kwargs=kwargs):
                pages = [
                    self._generate_page_soup(1),
                    self._generate_page_soup(21),
                    self._generate_page_soup(41, count=1, has_next=False),
                ]
                with patch.object(gc, "_request", side_effect=pages) as request:
                    caches = list(method(**kwargs))
                self.assertEqual([c.wp for c in caches], ["GC{:X}".format(i) for i in range(1, 42)])
                self.assertTrue(all(c.visited == datetime.date(2026, 10, 15) for c in caches))
                expected = [call(url)]
                for first in [1, 21]:
                    expected.append(
                        call(
                            url,
                            method="POST",
                            data={
                                "__EVENTTARGET": "ctl00$ContentBody$pgrTop$ctl08",
                                "__EVENTARGUMENT": "",
                                "__VIEWSTATE": "state-{}".format(first),
                                "__VIEWSTATEGENERATOR": "85D312FD",
                            },
                        )
                    )
                self.assertEqual(request.call_args_list, expected)

    def test_limit(self):
        gc = Geocaching()
        for limit, requests in [(0, 0), (3, 1), (20, 1), (21, 2), (40, 2)]:
            with self.subTest(limit=limit):
                with patch.object(
                    gc, "_request", side_effect=[self._generate_page_soup(1), self._generate_page_soup(21)]
                ) as request:
                    self.assertEqual(len(list(gc.my_finds(limit))), limit)
                self.assertEqual(request.call_count, requests)

    def test_no_logs(self):
        gc = Geocaching()
        with patch.object(gc, "_request", return_value=BeautifulSoup("No results found.", "html.parser")) as request:
            self.assertEqual(list(gc.my_finds()), [])
        request.assert_called_once_with("my/logs.aspx?lt=2")


class TestAdvancedSearch(LoggedInTest):
    def test_search(self):
        with self.recorder.use_cassette("advanced_search"):
            # https://www.geocaching.com/play/search?st=Prague%2C+Hlavní+město+Praha&ot=query&asc=false&sort=distance
            results = self.gc.advanced_search(
                options={
                    "st": "Prague, Hlavní město Praha",
                    "ot": "query",
                    "asc": "false",
                    "sort": "distance",
                },
                limit=50,
            )
            self.assertEqual("GC11JM6", list(results)[0].wp)

    def test_caches_owned_by_geocaching_hq(self):
        with self.recorder.use_cassette("advanced_search_caches_owned_by_hq"):
            # https://www.geocaching.com/play/search/?hb=Geocaching+HQ
            options = {"hb": "Geocaching HQ"}
            generator = self.gc.advanced_search(options=options)
            results = list(generator)
            self.assertGreaterEqual(91, len(results))
            self.assertEqual("GC1TEZH", results[-1].wp)


class TestAPIMethods(LoggedInTest):
    def test_search_rect(self):
        """Perform search by rect and check found caches."""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.39))

        expected = {"GC161KR", "GCA29DP", "GCZC5D", "GC11PRW", "GC7JRR5", "GC7KDWE", "GC1GW54"}

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
                            # can happen when getting accurate location
                            continue
                    self.assertEqual(distances, sorted(distances))

                with self.subTest("sort by distance reverse"):
                    origin = Point.from_string("N 49° 44.230 E 013° 22.858")
                    caches = list(self.gc.search_rect(rect, sort_by=SortOrder.distance, reverse=True, origin=origin))
                    waypoints = {cache.wp for cache in caches}
                    self.assertSetEqual(waypoints, expected)

                    # Check if caches are reverse sorted by distance to origin
                    distances = []
                    for cache in caches:
                        try:
                            distances.append(great_circle(cache.location, origin).meters)
                        except PMOnlyException:
                            # can happen when getting accurate location
                            continue
                    self.assertEqual(distances, sorted(distances, reverse=True))

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
