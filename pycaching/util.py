#!/usr/bin/env python3

import re


class Util(object):

    _rot13codeTable = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM")

    @staticmethod
    def parseRaw(raw):
        """Parses the coords in Degree Minutes format. Expecting:

        S 36 51.918 E 174 46.725 or
        N 6 52.861  W174   43.327

        Spaces do not matter. Neither does having the degree symbol.

        Returns a two tuples in dm format."""

        # Make it uppercase for consistency
        coords = raw.upper().replace("N", " ").replace("S", " ") \
            .replace("E", " ").replace("W", " ").replace("+", " ")

        try:
            m = re.match(r"\s*(-?\s*\d+)\D+(\d+[\.,]\d+)\D?\s*(-?\s*\d+)\D+(\d+[\.,]\d+)", coords)

            latDeg, latMin, lonDeg, lonMin = [float(part.replace(" ", "").replace(",", ".")) for part in m.groups()]

            if "S" in raw:
                latDeg *= -1
            if "W" in raw:
                lonDeg *= -1

            return ((latDeg, latMin), (lonDeg, lonMin))

        except AttributeError:
            raise ValueError("Could not parse the coordinates entered manually.")

    @staticmethod
    def rot13(text):
        """Returns a text encoded by rot13 cipher."""
        return str.translate(text, Util._rot13codeTable)

    @staticmethod
    def toDecimal(deg, min):
        """Returns a decimal interpretation of coordinate in MinDec format."""
        return round(deg + min / 60, 5)

    @staticmethod
    def toMinDec(decimal):
        """Returns a DecMin interpretation of coordinate in decimal format."""
        return int(decimal), round(60 * (decimal - int(decimal)), 3)
