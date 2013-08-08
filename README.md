# PyCaching - Geocaching.com website crawler

A Python interface for working with Geocaching.com website. I've used some code from two packages:

- Geocache Grabber (by Fuad Tabba) - http://www.cs.auckland.ac.nz/~fuad/geo.py
- geocaching-py (by Lev Shamardin) - https://github.com/abbot/geocaching-py

## Features
- login to Geocaching.com
- search for up to 200 Caches by any Point
- load Cache details by WP
- _more coming soon_

## Requirements
- BeautifulSoup >= 3.2.1
- geopy >= 0.95.1

## Example usage


    import pycaching

    geocaching = pycaching.login("user", "pass")
    cache = geocaching.loadCache("GC12345")
    print cache["name"]

## Legal notice

Be sure to read Geocaching.com's terms of use (http://www.geocaching.com/about/termsofuse.aspx). By using this piece of software you break them and your Geocaching account may be suspended or even deleted. To prevent this, I recommend you to load the data you really need, nothing more. This software is provided "as is" and I am not responsible for any damage possibly caused by it.

## Author

Tomas Bedrich  
tbedrich.cz  
ja@tbedrich.cz
