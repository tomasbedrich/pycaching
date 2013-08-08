from distutils.core import setup
from pycaching.version import version

setup(    
    name='PyCaching',
    version=version,
    author='Tomas Bedrich',
    author_email='ja@tbedrich.cz',
    packages=['pycaching',],
    license='GNU Lesser General Public License (LGPL)',
    description='Geocaching.com site crawler. Searches and loads caches.',
    long_description=open('README.txt').read(),
    install_requires=[
	    "BeautifulSoup >= 3.2.1",
	    "geopy == 0.95.1",
	],
)