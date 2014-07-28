#!/usr/bin/env python3

import unittest
import logging

from pycaching import Util


class TestUtil(unittest.TestCase):

    def test_parseRaw(self):
        self.assertEqual(Util.parseRaw("N 49 45.123 E 013 22.123"), ((49, 45.123), (13, 22.123)))
        self.assertEqual(Util.parseRaw("S 49 45.123 W 013 22.123"), ((-49, 45.123), (-13, 22.123)))
        self.assertEqual(Util.parseRaw("N49 45.123 E013 22.123"), ((49, 45.123), (13, 22.123)))
        self.assertEqual(Util.parseRaw("49N 45.123 013E 22.123"), ((49, 45.123), (13, 22.123)))
        self.assertEqual(Util.parseRaw("49S 45.123 013W 22.123"), ((-49, 45.123), (-13, 22.123)))
        self.assertEqual(Util.parseRaw("N 49 45,123 E 013 22,123"), ((49, 45.123), (13, 22.123)))
        self.assertEqual(Util.parseRaw("N 49° 45.123 E 013° 22.123"), ((49, 45.123), (13, 22.123)))
        self.assertEqual(Util.parseRaw("N 49 45.123, E 013 22.123"), ((49, 45.123), (13, 22.123)))
        self.assertEqual(Util.parseRaw("N 49 45.000 E 13 0.0"), ((49, 45), (13, 0)))
        self.assertRaises(ValueError, Util.parseRaw, "123")

    # @unittest.skip("tmp")
    def test_urlopen(self):
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile("w") as tmp:
            tmp.file.write("Hello World!")
            tmp.file.flush()
            data = Util.urlopen("file://" + tmp.name).read().decode().strip()
            self.assertEqual(data, "Hello World!")

    def test_rot13(self):
        self.assertEqual(Util.rot13("Text"), "Grkg")
        self.assertEqual(Util.rot13("abc'ř"), "nop'ř")

    def test_coordConversion(self):
        self.assertEqual(Util.toDecimal(49, 43.850), 49.73083)
        self.assertEqual(Util.toDecimal(13, 22.905), 13.38175)
        self.assertEqual(Util.toMinDec(13.38175), (13, 22.905))
        self.assertEqual(Util.toMinDec(49.73083), (49, 43.850))


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
