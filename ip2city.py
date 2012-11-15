#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import json
from pygeoip import GeoIP, GeoIPError, MEMORY_CACHE
from argparse import ArgumentParser
from werkzeug.serving import run_simple
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

class ip2city(object):

    stats = {
        'requests': 0,
        'successes': 0,
        'errors': 0,
    }

    geoip_v4 = None
    geoip_v6 = None


    def __init__(self, database, database_v6):
        self.url_map = Map([
            Rule('/', endpoint='resolve'),
            Rule('/favicon.ico', endpoint='favicon'),
            Rule('/status', endpoint='status'),
        ])
        self.geoip_v4 = GeoIP(database, MEMORY_CACHE)
        if database_v6:
            self.geoip_v6 = GeoIP(database_v6, MEMORY_CACHE)


    # Serve empty favicon.ico
    def on_favicon(self, request):
        return Response()


    def on_status(self, request):
        response = self.stats
        response['status'] = 'Working for you.'
        return Response(json.dumps(response))


    def on_resolve(self, request):
        ip = request.args.get('ip')
        self.stats['requests'] += 1
        record = {}

        try:
            if ':' in ip:
                if self.geoip_v6:
                    record = self.geoip_v6.record_by_addr(ip)
                    self.stats['successes'] += 1
                else:
                    self.stats['errors'] += 1
            else:
                record = self.geoip_v4.record_by_addr(ip)
                self.stats['successes'] += 1
        except GeoIPError, e:
            print e
            self.stats['errors'] += 1

        return Response(json.dumps(record))


    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        return getattr(self, 'on_' + endpoint)(request, **values)


    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)


    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def parse_args():
    parser = ArgumentParser(description='Face detection web service')
    parser.add_argument('--hostname', '-H', type=str, default='localhost',
                        help='Hostname to bind service to')
    parser.add_argument('--port', '-p', type=int, default=5000,
                        help='Port to bind service to')
    parser.add_argument('--database', '-D', type=str,
                        default='GeoLiteCity.dat',
                        help='Path to GeoIP database for IPv4')
    parser.add_argument('--database-v6', '-6', type=str, dest='database_v6',
                        help='Path to GeoIP database for IPv6')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debugging')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    try:
        app = ip2city(args.database, args.database_v6)
    except IOError, e:
        print e.strerror + ': ' + e.filename
        sys.exit(1)

    run_simple(args.hostname, args.port, app, use_debugger=args.debug,
               use_reloader=args.debug)
