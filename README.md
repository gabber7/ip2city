ip2city
==========

Webservice to resolve ip addresses to cities


Requirements
-------------

Werkzeug
argparse
pygeoip

HowTo (Debian)
---------------

git clone git://github.com/gabber7/ip2city.git
cd ip2city
pip install -r requirements.txt
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
gunzip GeoLiteCity.dat.gz
python ip2city.py --host=0.0.0.0 --port=5000 --database=GeoLiteCity.dat

Usage
------

Send HTTP request with ip as argument
