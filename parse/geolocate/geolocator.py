#!python
import urllib
import urllib2
import json


class GeocoderError(Exception):
    pass


class GeocoderResultError(Exception):
    pass


base_url = "http://maps.googleapis.com/maps/api/geocode/json?&%s"


def geocode(address, latlng):
    params = {'address': address, 'sensor': "false"}
    if latlng is not None:
        params['latlng'] = latlng
    url = base_url % urllib.urlencode(params)
    data = urllib2.urlopen(url)

    response = json.loads(data.read())

    if 'status' in response and response['status'] == 'OK':
        return response['results'][0]
    else:
        return {}