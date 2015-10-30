#!/usr/bin/env python3

import pycaching
from pycaching import Cache, Log, LogType
from datetime import date


_username, _password = "user", "pass"
codes = ["GC2Z3XG", "GC5APPG", "GC5PZJG", "GC5HX18", "GC5CTGT", "GC5PZWC", "GC5PZVY", "GC364M8", "GC4MW12", "GC4Z6NN", "GC5PZW3", "GC5PZWZ", "GC1VZTH", "GC4X62Z", "GC40YR3", "GC5PZHX"]

l = Log(type=LogType.found_it, text="Nalezeno v rámci tělocviku na ČVUT. Díky za kešku.", visited=date.today())

g = pycaching.login(_username, _password)
for code in codes:
    c = Cache(g, code)
    c.post_log(l)
    print("logged", code)
