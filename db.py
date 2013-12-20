#!python
""" This file contains the db models for eventizer
"""
from datetime import datetime
import json
import sqlite3
import os
from time import time
from common import event

get_rounded_time = lambda: int(time() / 10)


class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


# DB -----------------------------------------------------------------------------------------------------------
def conn(name, initial_insert_sql):
    db_path = os.path.dirname(os.path.realpath(__file__)) + '/db/{}'.format(name)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    for statement in initial_insert_sql:
        cursor.execute(statement)
    return connection, cursor


db_conn, db = conn('events.db', '''
        CREATE TABLE IF NOT EXISTS rejects
            ( eventid text CONSTRAINT eventid PRIMARY KEY ASC ON CONFLICT FAIL
            , data text )
    ---
        CREATE TABLE IF NOT EXISTS events
            ( eventid text CONSTRAINT eventid PRIMARY KEY ASC ON CONFLICT FAIL
            , data text )
    ---
        CREATE TABLE IF NOT EXISTS pre
            ( data text CONSTRAINT eventid PRIMARY KEY ASC ON CONFLICT IGNORE
            , time number )
    --- CREATE INDEX IF NOT EXISTS time ON pre (time)

    --- CREATE TABLE IF NOT EXISTS keywords (keyword text, eventid text)
    --- CREATE INDEX IF NOT EXISTS keyword ON keywords (keyword)

    --- CREATE TABLE IF NOT EXISTS keywords (keyword text, eventid text)
    --- CREATE INDEX IF NOT EXISTS keyword ON keywords (keyword)

    --- CREATE TABLE IF NOT EXISTS log (date text, name text, info text)

    --- CREATE TABLE IF NOT EXISTS addresses (address text, info text)
    --- CREATE INDEX IF NOT EXISTS address ON addresses (address)
    '''.split('---'))


# PRE ---------------------------------------------------------------------------------------------------------
def insert_pre(event_data, commit=True):
    data = json.dumps(event_data._asdict())
    db.execute("INSERT INTO pre (data, time) VALUES (?, ?)", (data, get_rounded_time()))
    if commit:
        db_conn.commit()


# REJECTS -----------------------------------------------------------------------------------------------------
def insert_reject(eventid, event_data, commit=True):
    event_data = DateTimeJSONEncoder().encode(event_data._asdict())
    db.execute("REPLACE INTO rejects (eventid, data) VALUES (?, ?)", (eventid, event_data))
    if commit:
        db_conn.commit()


def find_reject(prototype=None):
    return find_event(prototype, connection=db)


def probe_rejects(field):
    return dict(map(lambda i: (i.get('name'), i.get('raw', {}).get(field, '')), find_reject()))


# EVENTS ------------------------------------------------------------------------------------------------------
def insert_event(eventid, event_data, commit=True):
    q = "REPLACE INTO events VALUES (?, ?)"
    event_data = DateTimeJSONEncoder().encode(event_data._asdict())
    db.execute(q, (eventid, event_data))
    if commit:
        db_conn.commit()


def get_event(eventid):
    """
    >>> get_event("INVALID KEY")

    >>> insert_event("ID0001", event(name='Correct'), commit=False)
    >>> get_event("ID0001") == event(name='Correct')
    True
    """
    q = '''
        SELECT data
        FROM events
        WHERE eventid = ?
        '''
    db.execute(q, [eventid])
    results = db.fetchone()
    if results:
        return event(**json.loads(results[0]))


def find_event(prototype=None, connection=None):
    if connection is None:
        connection = db

    def matching(value1, value2):
        if type(value1) is str:
            return value1.lower() in value2.lower()
        elif type(value1) in [int, float]:
            return value1 == value2
        elif type(value1) is list:
            return min(map(lambda i: True in map(lambda j: matching(i, j), value2), value1))
        elif type(value1) is dict:
            return min(matching(value, value2.get(key, '')) for key, value in value1.iteritems())

    #noinspection PyShadowingNames
    def find_event_full(prototype):
        q = '''
            SELECT data
            FROM events
            '''
        connection.execute(q)
        for result in connection:
            event = json.loads(result[0])
            if prototype is None or matching(prototype, event):
                yield event

    #noinspection PyShadowingNames
    def find_event_filter(prototype):
        for event in find_event_full(prototype):
            del event['site_info']
            yield event

    return find_event_filter(prototype)


# KEYWORDS ------------------------------------------------------------------------------------------------------
def insert_keywords(keyword_generator, event_id, commit=True):
    values = ((keyword, event_id) for keyword in keyword_generator)
    db.executemany("REPLACE INTO keywords (keyword, eventid) VALUES (?, ?)", values)
    if commit:
        db_conn.commit()


def get_keyword_count(keyword):
    """
    >>> get_keyword_count("~~~~")

    >>> insert_keywords(("yeah",), "fairgrounds", False)
    >>> get_keyword_count("yeah")
    1
    """
    q = '''
        SELECT keyword, COUNT(*) as c
        FROM (
            SELECT DISTINCT keyword, eventid
            FROM keywords
            WHERE keyword = ?
        )
        GROUP BY keyword
        '''
    db.execute(q, [keyword])
    results = db.fetchone()
    if results:
        return results[1]


# ADDRESS ------------------------------------------------------------------------------------------------------
def address_cached_get(input_address, func, commit=True):
    """
    >>> address_cached_get("yo", lambda a: {u'lat': 3, u'lng': 5}, False)
    {u'lat': 3, u'lng': 5}
    >>> address_cached_get("yo", lambda a: {u'lat': 12, u'lng': 12}, False)
    {u'lat': 3, u'lng': 5}
    """
    q = 'SELECT * FROM addresses where address = ?'
    db.execute(q, [input_address])
    result = db.fetchone()
    if result:
        return json.loads(result[1])
    else:
        result = func(input_address)
        if result is None:
            return None
        else:
            db.execute("REPLACE INTO addresses VALUES (?, ?)", (input_address, json.dumps(result)))
            if commit:
                db_conn.commit()
            return result


# LOG ------------------------------------------------------------------------------------------------------
def log(msg):
    db.execute('''INSERT INTO log (date, name, info) VALUES (?, ?, ?)''',
               (datetime.datetime.now(), __name__, msg))
    db_conn.commit()


def err(msg):
    log(msg)
