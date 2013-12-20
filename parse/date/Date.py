from datetime import timedelta, datetime
from collections import namedtuple


class Date(namedtuple('Date', 'year month day weekday hour am_pm minute second')):
    def __new__(cls, year=None, month=None, day=None, weekday=None, hour=None, am_pm=None, minute=None, second=None):
        return super(Date, cls).__new__(cls, year, month, day, weekday, hour, am_pm, minute, second)

    def update(self, other):
        if hasattr(other, '_asdict'):
            fields = [(k, v) for k, v in other._asdict().items() if v is not None]
            return self._replace(**dict(fields))
        else:
            raise TypeError('Method only works with namedtuples')


def timedelta_from_Date(date1, date2):
    """ Generate a timedelta from two dates,
    or None if one could not be generated.

    Operates on time if either do not have a date.
    Does not work with weeks, though timedelta supports this,
    it is meant for hours only.

    TODO: Does not work if the date is across two different months.
    Perhaps before doing date operations that are too big, just
    Check to see if they are in the same month, and if they are not
    just add the last day of that month to the date and subtract to get days.
    TODO: Does not check if the second date is bigger. It is assumed
    We need to check if the second date it bigger.
    >>> timedelta_from_Date(Date(hour=1), Date(hour=2))
    datetime.timedelta(0, 3600)
    """
    time_region_names = ["day", "hour", "minute", "second"]
    time_regions = {}
    (date1, date2) = (date1._asdict(), date2._asdict())
    for name in time_region_names:
        if date1[name] is not None and date2[name] is not None:
            time_regions[name + 's'] = date2[name] - date1[name]
    return timedelta(**time_regions)


def to_datetime(date_dict, year, month, day):
    """
    >>> to_datetime({"day":1}, 2012, 6, 15)
    datetime.datetime(2012, 6, 1, 0, 0)
    >>> to_datetime({"day":1, "month": 5}, 2012, 6, 15)
    datetime.datetime(2012, 5, 1, 0, 0)
    """
    if isinstance(date_dict, datetime):
        return date_dict
    valid_items = ["year", "month", "day", "hour", "minute", "second"]
    for required_name, value in {"year": year, "month": month, "day": day}.iteritems():
        if required_name not in date_dict or date_dict[required_name] is None:
            date_dict[required_name] = value
    return datetime(**dict((k, v) for k, v in date_dict.iteritems() if k in valid_items and v is not None))


def to_datetime_with_today(date_dict):
    today = datetime.today()
    return to_datetime(date_dict, today.year, today.month, today.day)