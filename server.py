__author__ = 'Joel Haasnoot'

import urllib
import requests
import simplejson as json

try:
    from config import *
except:
    # ENDPOINT_URL = 'http://localhost:8080'
    ENDPOINT_URL = 'http://api.navitia.io/v1/journeys'
    COMMON_HEADERS = [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]

def notfound(start_response):
    start_response('404 File Not Found', COMMON_HEADERS + [('Content-length', '2')])
    yield '[]'

def decode_url(input):
    return urllib.unquote(input)

def reverse_loc(input):
    lat, lon = decode_url(input).split(',')
    return lon+';'+lat

def map_navitia_input(params):
    return {'from': reverse_loc(params['from-latlng']),
            'to': reverse_loc(params['to-latlng']),
            'datetime': decode_url(params['date']).replace('-', '').replace(':', '')}

def map_navitia_output(response):
    return response

def parse_url(url):
    # https://1313.nl/rrrr?depart=true&from-latlng=51.985081%2C5.900028&to-latlng=51.948341%2C4.434145&date=2014-04-26T20%3A02%3A20&showIntermediateStops=true
    return {entry.split('=')[0]: entry.split('=')[1] for entry in url.split('&')}

def application(environ, start_response):
    if environ['PATH_INFO'][1:] != 'otp-facade':
        return notfound(start_response)

    parameters = parse_url(environ['QUERY_STRING'])
    intermediary_params = map_navitia_input(parameters)
    pieces = '&'.join([k+'='+v for k,v in intermediary_params.items()])

    url = ENDPOINT_URL+'?'+pieces
    response = requests.get(url)
    if response.status_code == 200:
        reply = json.dumps(map_navitia_output(response.json()), indent=4 * ' ')
    else:
        reply = ""

    start_response('200 OK', COMMON_HEADERS + [('Content-length', str(len(reply)))])
    return reply