# PyCaching - Geocaching for Python

A Python interface for working with Geocaching.com website. I've used some code from two packages:

- Geocache Grabber (by Fuad Tabba) - http://www.cs.auckland.ac.nz/~fuad/geo.py
- geocaching-py (by Lev Shamardin) - https://github.com/abbot/geocaching-py

## Features
- login to Geocaching.com
- search for up to 200 caches around any point
- load cache details by WP (2 ways)
- utils for coordinate sanitization, rot13 conversion
- _more coming soon_

## Requirements
- BeautifulSoup >= 3.2.1
- geopy >= 0.95.1

## Example usage

### Load one cache details

    import pycaching

    geocaching = pycaching.login("user", "pass")
    cache = geocaching.loadCache("GC12345")
    print cache["name"]

### Find all traditional caches around

    import pycaching
    import geopy
    
    point = geopy.Point(10.123456, 10.123456)

    geocaching = pycaching.login("user", "pass")
    caches = geocaching.search(point)
    for cache in caches:
        if cache["type"] == "Traditional Cache"
            print cache["wp"]

### Find all caches on some adress

    import pycaching
    import geopy
    from geopy import geocoders
    
    place, (lat, lng) = geocoders.GoogleV3().geocode("10900 Euclid Ave in Cleveland")
    point = geopy.Point(lat, lng)
    
    geocaching = pycaching.login("user", "pass")
    caches = geocaching.search(point)
    for cache in caches:
        print cache["wp"]

## Legal notice

Be sure to read Geocaching.com's terms of use (http://www.geocaching.com/about/termsofuse.aspx). By using this piece of software you break them and your Geocaching account may be suspended or even deleted. To prevent this, I recommend you to load the data you really need, nothing more. This software is provided "as is" and I am not responsible for any damage possibly caused by it.

## Author

Tomas Bedrich  
www.tbedrich.cz  
ja@tbedrich.cz
