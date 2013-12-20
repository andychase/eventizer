"""
Common includes the base event schema, and some functions to deal with storing/loading data.

There is a strict schema, you can't just insert into any field:
>>> try: print event(bad_field="Should cause assertion")
... except KeyError: print "Event Assertion Received"
Event Assertion Received
"""
import sys
import json
import traceback
import os
from random import randrange
import pipeless

event_schema = {
    'id': "",  # DateHash_Geohash
    'name': "",
    'date': "",
    'address': "",
    'venue_name': "",
    'type': "",
    'location': "",
    'keywords': "",
    'description': "",
    'raw': {},
    'sources': [],
    'scores': {},
    'score': 1,
    'site_info': {},
    'url': "",
    'html': "",
}


event = pipeless.namedtuple_optional(event_schema, 'event')


def export_exception(event, exception):
    try:
        if 'name' in event.site_info:
            event = event._replace(site_info=event.site_info['name'])
        event = event._replace(html='')
        msg = {
            'error': exception.message,
            'stack': traceback.format_exc().split("\n"),
            'event': dict(event._asdict()),
            'args': sys.argv
        }
        if not os.path.isdir('err'):
            os.mkdir('err')
        with open("err/e_" + str(randrange(0, 10000000)), "a") as f:
            json.dump(msg, f)
        sys.stderr.write('!')
        sys.stderr.flush()
    except:
        pass


def unicode_to_whitespace(string):
    """
    >>> unicode_to_whitespace(u'January\u00a011')
    'January 11'
    """

    def whitespace(string):
        for char in string:
            if ord(char) > 128:
                yield ' '
            else:
                yield char

    return "".join(whitespace(string)).encode('ascii')
