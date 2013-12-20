import pipeless
from common import unicode_to_whitespace, export_exception
from data import get_site_list

# Options
untitled_event_name = 'Untitled Event'
offline = False  # <- Operate in a mode that doesn't hit internet
# Setup
function, run, _ = pipeless.pipeline()  # export_exception
command, cli = pipeless.commandline(__doc__)


@command
def online():
    list(run(crawl()))


@command
def test():
    from common import event
    import json

    global offline
    offline = True

    def out_events():
        with open('out', 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line is not '':
                    yield event(**json.loads(line))

    list(run(out_events()))


# Output ----------------------------------------------------------------------------------------------------------
def crawl():
    from grab.crawler import site_map
    site_map(get_site_list().values())

    for crawling_session in site_map(get_site_list().values()):
        for item in crawling_session:
            yield item


@function('output')
def scrape():
    from output.scraper import scrape as html_scraper
    from output.ical import ical_scraper
    site_list = get_site_list()

    def func(event):
        if offline:
            # Refresh site list because crawling sometimes gets cached for testing
            if event.site_info['name'] in site_list:
                event = event._replace(site_info=site_list[event.site_info['name']])

        if event.site_info.get('scrape', '') == 'ical | html':
            for ical_result in ical_scraper(event.html, event.site_info):
                html_result = html_scraper(ical_result['raw']['description'], event.site_info)
                ical_result['raw'].update(html_result['raw'])
                url = ical_result['raw'].get('url', '')
                yield event._replace(html="", url=url, **ical_result)
        else:
            data = html_scraper(event.html, event.site_info)
            yield event._replace(html="", **data)

    return func


# Parse -----------------------------------------------------------------------------------------------------------
@function('parse')
def address():
    from parse.geolocate.geolocator import geocode
    from db import address_cached_get
    import time
    import regex

    search_focus_lat_lng = "45.181374, -123.27866, 45.798472, -122.019352"
    offline_location = {'geometry': {'location': {'lat': 45.181374, 'lng': -123.27866}}}

    def fix_address_location(date_address, site_info):
        site_location = site_info.get('location', '')
        location_in_address = regex.search(
            '\b{}\b'.format(site_location),
            date_address
        )

        if date_address and site_location and not location_in_address:
            return date_address + ' ' + site_location
        return date_address

    def sleep_and_google(address):
        time.sleep(1)
        return geocode(address, search_focus_lat_lng)

    def func(event):
        address = fix_address_location(event.raw.get('address', ''), event.site_info)
        if not address:
            return event
        if offline:
            location = address_cached_get(address, lambda _: offline_location, commit=False)
        else:
            location = address_cached_get(address, sleep_and_google)
        location = location.get('geometry', {}).get('location', {})
        lat, lng = location.get('lat', None), location.get('lng', None)
        if lat and lng:
            return event._replace(address=address, location={'lat': lat, 'lon': lng})
        else:
            return event._replace(address=address)

    return func


@function('parse')
def date():
    from parse.date.functions import functions
    from collections import Iterable
    patterns_path = "parse/date/patterns.yaml"
    expressions_path = "parse/date/expressions.yaml"
    from reparse.builders import build_parser_from_yaml

    date_parser = build_parser_from_yaml(functions, expressions_path, patterns_path)

    def func(event):
        parse_date = event.raw.get('date', '')
        if isinstance(parse_date, Iterable):
            return event._replace(date=parse_date)
        # Combine dates if we scraped an 'date_end'
        if 'date_end' in event.raw and event.raw['date_end']:
            parse_date = "{} to {}".format(event.raw['date'], event.raw['date_end'])
        new_date = date_parser(unicode_to_whitespace(parse_date))
        # Convert to dict and insert if we retrieved a date
        if new_date is not None:
            new_date_dict = map(lambda l: l._asdict(), new_date)
            return event._replace(date=new_date_dict)
        else:
            return event

    return func


@function('parse')
def description():
    from output.scraper import trim_extra
    max_word_count = 50
    strip = lambda f: trim_extra(f.lstrip(",.[]()-=_+<>").strip())

    def shorten_longer(description):
        if len(description.split(" ")) > max_word_count:
            return " ".join(description.split(" ")[:max_word_count]) + "..."
        return description

    def func(event):
        description = shorten_longer(strip(event.raw.get('description', '')))

        name = strip(event.raw.get('name', '')).title()
        return event._replace(description=strip(description), name=strip(name).title())

    return func


@function('parse')
def category():
    from parse.category.categorize import categorize_event
    from parse.category.fix_names import build_category_fixer
    from data import get_categories
    category_fixer = build_category_fixer(get_categories())

    def func(event):
        category = event.raw.get('type', '').strip().lower()
        category = category_fixer(category)
        if category == "":
            category = categorize_event(event.description).lower()
        return event._replace(type=category)

    return func


@function('parse')
def keywords():
    from parse.keywords import get_keywords

    def func(event):
        return event._replace(keywords=get_keywords(event.description))

    return func


# Resolve ---------------------------------------------------------------------------------------------------------
@function('resolve')
def incomplete():
    from parse.date.Date import to_datetime_with_today
    from db import insert_reject
    has_date = lambda event: event.date and len(event.date) and to_datetime_with_today(event.date[0])
    has_address = lambda event: event.address and event.location and event.location.get('lat', False)

    def fix_name(event):
        if event.name.strip() is '':
            return event._replace(name=untitled_event_name)
        return event

    def func(event):
        if has_date(event) and has_address(event):
            return fix_name(event)
        else:
            insert_reject(hash(str(event)), event)
    return func


@function('resolve')
def ids():
    from time import mktime
    from resolve.geohash import encode as geo_encode
    from resolve.base_convert import int2base
    from parse.date.Date import to_datetime_with_today
    geohash = lambda event: geo_encode(latitude=float(event.location['lat']), longitude=float(event.location['lon']))
    date_to_int = lambda d: int(mktime(d.timetuple()))
    int_to_base32 = lambda i: int2base(i, 32)
    date_hash = lambda event: int_to_base32(date_to_int(to_datetime_with_today(event.date[0])))

    date_geohash_template = "{date}_{geo}".format

    def func(event):
        if event.location is not None and event.date is not None and len(event.date):
            return event._replace(id=date_geohash_template(date=date_hash(event), geo=geohash(event)))
    return func


@function('resolve')
def duplicates():
    """ Merge data from previous data
        TODO: picking the best data
    """
    from db import get_event, insert_event

    def func(event):
        pre_existing = get_event(event.id)
        if not pre_existing:
            insert_event(event.id, event)
            return event

    return func


# Scan ------------------------------------------------------------------------------------------------------------
@function('score')
def unique():
    from scan.unique import get_uniqueness

    def func(event):
        new_scores = event.scores.update({'uniqueness': get_uniqueness(event.keywords, event.name)})
        return event._replace(scores=new_scores)

    return func


# Send ------------------------------------------------------------------------------------------------------------
@function('send')
def search():
    import pycurl
    from parse.date.Date import to_datetime_with_today

    c = pycurl.Curl()
    import json

    valid_columns = ("_id sourceurl type description venue_name name source score "
                     "location address date type chunks oldid".split(" ")
                     )

    try:
        with open("endpoint", "r") as f:
            endoint_url = f.read().trim()
    except:
        print "Error getting endpoint url"

    def fix_id(event_dict):
        event_dict.update({
            "_id": event_dict['id'],
            "sourceurl": event_dict['url']
        })
        return event_dict

    enough_info = lambda event: isinstance(event.date, list) and event.address
    filter_columns = lambda event: dict([(k, v) for k, v in event.items() if k in valid_columns])
    event_to_str = lambda event: json.dumps(filter_columns(fix_id(event._asdict())))

    def post(event_str, event_id):
        if offline:
            print event_str
        else:
            c.setopt(c.URL, endoint_url.format(event_id))
            c.setopt(c.COPYPOSTFIELDS, event_str)
            c.perform()

    def func(event, post=post):
        if enough_info(event):
            for event_date in event.date:
                date = to_datetime_with_today(event_date).isoformat()
                name = unicode_to_whitespace(event.name)
                event = event._replace(date=date, name=name)
                post(event_to_str(event), event.id)

    return func


# Tools -----------------------------------------------------------------------------------------------------------
@command
def keys():
    spaced = lambda a: " ".join(a)
    empty = lambda v: v is None or len(v) == 0

    def func(event):
        event_items = event._asdict().items()
        print spaced(([k for k, v in event_items if not empty(v)]))
        return None
    return func


@command
def probe_rejects():
    from pprint import pprint
    from db import probe_rejects
    field = raw_input("field? ")
    pprint(probe_rejects(field))
    exit()


# UI --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    cli()
