"""
This file contains the parsing functions related to patterns

The point is that each function can take in a result tuple and
   use custom logic to parse a meaningful date group from it.
"""
from Date import Date, timedelta_from_Date


def progressive_match(string, possibilities):
    part = ""
    for character in string.lower():
        part += character
        matches = []
        for month, value in possibilities.iteritems():
            if part in month:
                matches.append(month)
        if len(matches) == 1:
            return possibilities[matches[0]]
    return None


def month_to_int(month_string):
    """ Converts English month to number.
        Cannot be misspelled. Handles any kind of abbr.
    >>> month_to_int("Jan")
    1
    >>> month_to_int("Sept.")
    9
    """
    month_list = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    return progressive_match(month_string, month_list)


def weekday_to_int(WeekdayString):
    weekday_list = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    return progressive_match(WeekdayString, weekday_list)


# Time Functions
def am_pm(input):
    if input.lower() == "am":
        return 0
    elif input.lower() == "pm":
        return 12


def military_time(MilHour, MilMinute, MilSecond):
    return time_expression(MilHour, MilMinute, MilSecond, None)


noon = lambda hour, AMPM: hour == 12 and AMPM == 12
midnight = lambda hour, AMPM: hour == 12 and AMPM == 0


def time_expression(Hour=None, Minute=None, Second=None, AMPM=None, SpecialTimeText=None):
    if SpecialTimeText:
        if SpecialTimeText.lower() == "noon":
            return Date(hour=12)
        if SpecialTimeText.lower() == "midnight":
            return Date(hour=0)
    d = Date()
    if Hour:
        d = d._replace(hour=int(Hour))
    if Minute:
        d = d._replace(minute=int(Minute))
    if Second:
        d = d._replace(second=int(Second))
    if AMPM is not None:
        if d.hour:
            if noon(d.hour, AMPM):
                d = d._replace(hour=12)
            elif midnight(d.hour, AMPM):
                d = d._replace(hour=0)
            else:
                d = d._replace(hour=d.hour + AMPM)
        d = d._replace(am_pm=AMPM)
    if (d.hour, d.minute, d.second) != (None, None, None):
        return d


def time_and_time(Hour=None, Minute=None, AMPM1=None, Hour2=None, Minute2=None, AMPM2=None):
    if AMPM2 is not "":
        AMPM2 = am_pm(AMPM2)
    if not AMPM1 and not AMPM2:
        return [time_expression(Hour=Hour, Minute=Minute), time_expression(Hour=Hour2, Minute=Minute2)]
    elif not AMPM1:
        return [time_expression(Hour=Hour, Minute=Minute, AMPM=AMPM2),
                time_expression(Hour=Hour2, Minute=Minute2, AMPM=AMPM2)]
    elif not AMPM2:
        return [time_expression(Hour=Hour, Minute=Minute, AMPM=AMPM1),
                time_expression(Hour=Hour2, Minute=Minute2, AMPM=AMPM1)]


# Date Functions

def month_type(input):
    for value in input:
        if value is not None:
            return int(value[0])


def date_number(Day=None, Abbr=None):
    if Day:
        return int(Day)


def month_number(MonthNum=None):
    return int(MonthNum)


def month_num_type(input):
    if type(input) is list:
        return int(input[0])
    else:
        return int(input)


def year(Year=None):
    if Year:
        return int(Year)

# Patterns #


def weekday_range_with_time(time1=None, time2=None, weekday1=None, weekday2=None, MonthRange=None):
    output = []
    if time1:
        for date in MonthRange:
            output.append(date.update(time1))
            if time2:
                output.append(date.update(time2))
    return output


def weekday_range_with_extra(
        time=None, and_time=None, weekday_start=None, weekday_end=None,
        extra_time=None, extra_weekday=None, MonthRange=None):
    output = []
    if time:
        for date in MonthRange:
            if hasattr(date, 'weekday'):
                if date.weekday in range(weekday_start, weekday_end + 1):
                    output.append(date.update(time))
                    if and_time:
                        output.append(date.update(and_time))
                if date.weekday == extra_weekday:
                    output.append(date.update(extra_time))
    return output


def weekday_range_with_extra_backwards(
        extra_time, extra_weekday, time, weekday_start, weekday_end,
        MonthRange):
    return weekday_range_with_extra(
        time[0], time[1], weekday_start, weekday_end,
        extra_time, extra_weekday, MonthRange)


def reverse_basic_text(time=None, day=None, month=None, year=None):
    return basic_text(time=time, day=day, month=month, year=year)


def basic_text(time=None, first_second=None, weekday=None,
               month=None, day=None, year=None):
    if not day:
        day = 1
    if not time:
        return Date(year=year, month=month, day=day)
    if time:
        date = Date(year=year, month=month, day=day)
        return date._replace(hour=time.hour, minute=time.minute, second=time.second, am_pm=time.am_pm)


def slash(month=None, day=None, year=None, time=None):
    return basic_text(time, None, None, month, day, year)


def month_range(month, Date1, Date2):
    output = []
    for i in range(Date1, Date2 + 1):
        output.append(basic_text(month=month, day=i))
    return output


def multi_time(time1, BasicText):
    output = []
    if time1 and BasicText:
        output.append(BasicText.update(time1))
        output.append(BasicText)
        return output


def large_repeat_words(*ThrowAwayAllVars):
    return None


def weekday_range_with_time_range(time1=None, weekday_range=None):
    output = []
    if time1 and weekday_range:
        range = timedelta_from_Date(weekday_range[0].update(time1), weekday_range[0])
        for weekday in weekday_range:
            output.append(weekday._replace(hour=time1.hour, minute=time1.minute, am_pm=time1.am_pm))
            output.append(range)
        return output


def time_range(unstrict_time={}, strict_time={}, date={}, reverse=False):
    endtime = date
    starttime = endtime
    if unstrict_time:
        starttime = starttime._replace(hour=int(unstrict_time[0]))
        if date.am_pm:
            starttime = starttime._replace(hour=starttime.hour + date.am_pm, am_pm=date.am_pm)
    else:
        starttime = starttime._replace(hour=strict_time.hour, minute=strict_time.minute)

    time_range = timedelta_from_Date(starttime, endtime)
    if reverse:
        time_range = timedelta_from_Date(endtime, starttime)
    return [starttime, time_range]


def alt_time_range(first_second=None, weekday=None, month=None, day=None, year=None, time=None, unstrict_time={}, strict_time={}):
    return time_range(unstrict_time, strict_time, basic_text(time, first_second, weekday, month, day, year), reverse=True)


def until_range(date1=None, date2=None):
    if date1 and date2:
        return [date1, timedelta_from_Date(date1, date2)]


def through_range(time=None, weekday1=None, weekday2=None, month=None, date=None, beginning=None):
    output = []
    if month and date and beginning and weekday1:
        ending = Date(month=month, day=date)
        for day in range(beginning.day, ending.day + 1):
            temp = Date(month=month, day=day)
            if temp.weekday and temp.weekday in range(weekday1, weekday2 + 1):
                if time:
                    output.append(temp.update(time))
                else:
                    output.append(temp)
        return output


# --------------- The lists ------------------
functions = {
    # Groups
    "MonthString": month_to_int,
    "AMPM": am_pm,
    # Expressions
    "Chase Year": year,
    "Chase Date": date_number,
    "Chase Month": month_number,
    "Steve Valaitis": time_expression,
    "Greg Burns": time_expression,
    "Greg Burns UnstrictTime:": time_expression,
    "Steve Valaitis2": military_time,
    "Steve Valaitis And Time": time_and_time,
    "Text Parts": time_expression,
    "Michael Ash10": weekday_to_int,
    # Types
    "Month": month_type,
    "MonthNum": month_num_type,
    # Patterns
    "LargeRepeatWords": large_repeat_words,
    "BasicText": basic_text,
    "ReverseBasicText": reverse_basic_text,
    "Slash": slash,
    "MonthRange": month_range,
    "MultiTime": multi_time,
    "WeekdayRangeWithTime": weekday_range_with_time,
    "WeekdayRangeWithExtra": weekday_range_with_extra,
    "WeekdayRangeWithExtraBackwards": weekday_range_with_extra_backwards,
    "WeekdayRangeWithTimeRange": weekday_range_with_time_range,
    "UntilRange": until_range,
    "ThroughRange": through_range,
    "TimeRange": time_range,
    "AltTimeRange": alt_time_range,
}
