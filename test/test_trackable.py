#!/usr/bin/env python3

import unittest
from datetime import date
from unittest import mock

from bs4 import BeautifulSoup

from pycaching import Geocaching, Trackable
from pycaching.errors import LoadError
from pycaching.errors import ValueError as PycachingValueError
from pycaching.log import Log
from pycaching.log import Type as LogType
from pycaching.util import format_date

from . import LoggedInTest


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.gc = Geocaching()
        self.t = Trackable(
            self.gc,
            "TB123AB",
            name="Testing",
            type="Travel Bug",
            location="in the hands of human",
            owner="human",
            description="long text",
            goal="short text",
            origin="Bayern, Germany",
            release_date="Sunday, 01 January 2017",
            last_logs=[],
        )
        self.t._log_page_url = "/track/details.aspx?id=6359246"

    def test___str__(self):
        self.assertEqual(str(self.t), "TB123AB")

    def test___eq__(self):
        self.assertEqual(self.t, Trackable(self.gc, "TB123AB"))

    def test_tid(self):
        self.assertEqual(self.t.tid, "TB123AB")

    def test_name(self):
        self.assertEqual(self.t.name, "Testing")

    def test_type(self):
        self.assertEqual(self.t.type, "Travel Bug")

    def test_owner(self):
        self.assertEqual(self.t.owner, "human")

    def test_location(self):
        self.assertEqual(self.t.location, "in the hands of human")

    def test_description(self):
        self.assertEqual(self.t.description, "long text")

    def test_goal(self):
        self.assertEqual(self.t.goal, "short text")

    def test_log_page_url(self):
        self.assertEqual(self.t._log_page_url, "/track/details.aspx?id=6359246")

    def test_origin(self):
        with self.subTest("state and country"):
            self.assertEqual(self.t.origin, "Bayern, Germany")
            self.assertEqual(self.t.origin_state, "Bayern")
            self.assertEqual(self.t.origin_country, "Germany")

        with self.subTest("country only"):
            self.t.origin = " Germany "
            self.assertEqual(self.t.origin, "Germany")
            self.assertEqual(self.t.origin_state, "")
            self.assertEqual(self.t.origin_country, "Germany")

        with self.subTest("unknown"):
            self.t.origin = ""
            self.assertEqual(self.t.origin_state, "")
            self.assertEqual(self.t.origin_country, "")

    def test_release_date(self):
        with self.subTest("valid date"):
            self.assertEqual(self.t.release_date, date(2017, 1, 1))

        with self.subTest("unparsable date"):
            self.t.release_date = "not a date"
            self.assertEqual(self.t.release_date, "")

        with self.subTest("missing date"):
            self.t.release_date = None
            self.assertEqual(self.t.release_date, "")

    def test_last_logs(self):
        self.assertEqual(self.t.last_logs, [])


class TestLogsFromDetailsPage(unittest.TestCase):
    def test_no_log_table(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        self.assertEqual(Trackable._get_logs_from_details_page(soup), [])

    def test_log_without_text(self):
        html = """
        <table class="TrackableItemLogTable Table">
            <tr class="Data BorderTop">
                <th><img src="/images/logtypes/75.png" title="Visited" /> 12/5/2018</th>
                <td><a href="https://www.geocaching.com/p/?guid=abc">someone</a> took it to somewhere</td>
                <td>Bayern, Germany</td>
                <td><a href="https://www.geocaching.com/track/log.aspx?LUID=1234-abcd">Visit Log</a></td>
            </tr>
            <tr class="Data BorderBottom">
                <td colspan="4"><div class="TrackLogText markdown-output"></div></td>
            </tr>
        </table>
        """
        logs = Trackable._get_logs_from_details_page(BeautifulSoup(html, "html.parser"))

        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].uuid, "1234-abcd")
        self.assertEqual(logs[0].type, LogType.visit)
        self.assertEqual(logs[0].visited, date(2018, 12, 5))
        self.assertEqual(logs[0].author, "someone")
        self.assertEqual(logs[0].text, "")


class TestMethods(LoggedInTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.t = Trackable(cls.gc, "TB1KEZ9")
        with cls.recorder.use_cassette("trackable_setup"):
            cls.t.load()

    def test_load(self):
        with self.subTest("tid"):
            trackable = Trackable(self.gc, "TB1KEZ9")
            with self.recorder.use_cassette("trackable_load_tid"):
                self.assertEqual("Lilagul #2: SwedenHawk Geocoin", trackable.name)

        with self.subTest("trackable url"):
            url = "http://www.geocaching.com/track/details.aspx?guid=cff00ac4-f562-486e-b303-32b2d01ed386"
            trackable = Trackable(self.gc, None, url=url)
            with self.recorder.use_cassette("trackable_load_url"):
                self.assertEqual("Lilagul #2: SwedenHawk Geocoin", trackable.name)

        with self.subTest("fail lazyload"):
            trackable = Trackable(self.gc, None)
            with self.assertRaises(LoadError):
                trackable.name

    def test_load_details(self):
        # self.t is loaded from the "trackable_setup" cassette
        self.assertEqual("lilagul", self.t.owner)
        self.assertEqual("In the hands of Alvis02.", self.t.location)
        self.assertEqual("Germany", self.t.origin)
        self.assertEqual("", self.t.origin_state)
        self.assertEqual("Germany", self.t.origin_country)
        self.assertEqual(date(2007, 5, 29), self.t.release_date)

    def test_load_last_logs(self):
        logs = self.t.last_logs
        self.assertEqual(10, len(logs))
        for log in logs:
            self.assertIsInstance(log, Log)
            self.assertIsInstance(log.type, LogType)

        newest = logs[0]
        self.assertEqual("af927434-392e-4cc9-a48a-89b5940f9e16", newest.uuid)
        self.assertEqual(LogType.discovered_it, newest.type)
        self.assertEqual(date(2017, 5, 30), newest.visited)
        self.assertEqual("smartdiver", newest.author)
        self.assertTrue(newest.text.startswith("Es ist an der Zeit"))

    def test_load_log_page(self):
        expected_types = {t.value for t in (LogType.grabbed_it, LogType.note, LogType.discovered_it)}
        expected_inputs = "__EVENTTARGET", "__VIEWSTATE"  # and more ...

        # make request
        with self.recorder.use_cassette("trackable_load_page"):
            valid_types, hidden_inputs, user_date_format = self.t._load_log_page()

        self.assertSequenceEqual(expected_types, valid_types)
        for i in expected_inputs:
            self.assertIn(i, hidden_inputs.keys())

        # user_date_format should not raise an exception when further processed
        format_date(date(2020, 12, 31), user_date_format)

    @mock.patch.object(Trackable, "_load_log_page")
    @mock.patch.object(Geocaching, "_request")
    def test_post_log(self, mock_request, mock_load_log_page):
        # mock _load_log_page
        valid_log_types = {
            # intentionally missing "grabbed it" to test invalid log type
            "4",  # write note
            "48",  # discovered it
        }
        mock_load_log_page.return_value = (valid_log_types, {}, "mm/dd/YYYY")
        test_log_text = "Test log."
        test_log_date = date.today()
        test_tracking_code = "ABCDEF"

        with self.subTest("empty log text"):
            log = Log(text="", visited=test_log_date, type=LogType.note)
            with self.assertRaises(PycachingValueError):
                self.t.post_log(log, test_tracking_code)

        with self.subTest("invalid log type"):
            log = Log(text=test_log_text, visited=test_log_date, type=LogType.grabbed_it)
            with self.assertRaises(PycachingValueError):
                self.t.post_log(log, test_tracking_code)

        with self.subTest("valid log"):
            log = Log(text=test_log_text, visited=test_log_date, type=LogType.discovered_it)
            self.t.post_log(log, test_tracking_code)

            # test call to _request mock
            expected_post_data = {
                "ctl00$ContentBody$LogBookPanel1$btnSubmitLog": "Submit Log Entry",
                "ctl00$ContentBody$LogBookPanel1$ddLogType": "48",  # discovered it - see valid_log_types
                "ctl00$ContentBody$LogBookPanel1$uxDateVisited": test_log_date.strftime("%m/%d/%Y"),
                "ctl00$ContentBody$LogBookPanel1$tbCode": test_tracking_code,
                "ctl00$ContentBody$LogBookPanel1$uxLogInfo": test_log_text,
            }
            mock_request.assert_called_with(self.t._log_page_url, method="POST", data=expected_post_data)

    def test_get_KML(self):
        with self.recorder.use_cassette("trackable_kml"):
            kml = self.t.get_KML()
        self.assertTrue('<?xml version="1.0" encoding="UTF-8"?>' in kml)
        self.assertTrue('<kml xmlns="http://earth.google.com/kml/2.2">' in kml)
        self.assertTrue("#tbTravelStyle" in kml)
        self.assertTrue("<visibility>1</visibility>" in kml)
        self.assertTrue("</Placemark></Document></kml>" in kml)


class TestIssues(LoggedInTest):
    def test_load__type(self):
        with self.subTest("existing"):
            trackable = Trackable(self.gc, "TB1KEZ9")
            with self.recorder.use_cassette("trackable_load__existing_type"):
                self.assertEqual("SwedenHawk Geocoin", trackable.type)

        with self.subTest("missing"):
            trackable = Trackable(self.gc, "TB7WZD9")
            with self.recorder.use_cassette("trackable_load__missing_type"):
                self.assertEqual(None, trackable.type)

    def test_load__origin_with_state(self):
        trackable = Trackable(self.gc, "TB7WZD9")
        with self.recorder.use_cassette("trackable_load__missing_type"):
            trackable.load()
        self.assertEqual("Bayern, Germany", trackable.origin)
        self.assertEqual("Bayern", trackable.origin_state)
        self.assertEqual("Germany", trackable.origin_country)
        self.assertEqual(date(2017, 1, 1), trackable.release_date)
        self.assertEqual("", trackable.last_logs[0].text)  # log without text
