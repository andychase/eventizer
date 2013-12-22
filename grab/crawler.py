#!python
import re
from time import time
import bs4
from gevent import sleep, monkey, queue
from gevent import pool as gevent_pool
from common import event
from link_util import should_download_link, fix_link, should_save_html

monkey.patch_all()
import urllib2

# Config
max_depth_to_parse = 2
website_sleep_time = 10
test_html = {'404': "<html>\n</html>"}

# Setup
pool = gevent_pool.Pool(20000)
events_retrieved = queue.Queue()

website_lasthit_time = {}

crawled_urls = {}

parse = lambda html: bs4.BeautifulSoup(html, "html5lib")


def add_crawled_urls(site_name, url):
    crawled_urls.setdefault(site_name, []).append(url)

in_crawled_urls = lambda site_name, url: url in crawled_urls.get(site_name, [])


def run_steps(steps, site_name, site_info):
    """
    >>> run_steps('print "hey"', 'yo', {})
    hey
    """
    get = lambda url: download_rate_limited(site_name, url, test=False)

    def scrape(url, **overrides):
        new_site_info = site_info.copy()
        new_site_info.update({
            'baseurl': url,
            'overrides': overrides,
            'steps': ''
        })
        prepare(new_site_info)
    exec steps in globals(), {'get': get, 'parse': parse, 'scrape': scrape}


def prepare(site_info, test=False):
    site_name = site_info.get('name', '*')
    steps = site_info.get('steps', '')
    if steps:
        run_steps(steps, site_name, site_info)
    else:
        crawl_only = re.compile(site_info['urlnosaveregex'])
        needed = re.compile(site_info['urlregex'])
        url = site_info['baseurl']
        crawl(url=url,
              site_info=site_info,
              site_name=site_name,
              crawl_only=crawl_only,
              needed=needed,
              depth=0,
              test=test)


def crawl(url, site_info, site_name, crawl_only, needed, depth, test=False):
    r"""
    >>> import re
    >>> from collections import namedtuple
    >>> e = namedtuple('event', 'html url site_info sources')("", "", {}, [])
    >>> crawl('http://example.org/', {'d':1, 'name': 'test'}, 'test', re.compile("0^"), re.compile(".+"), 0, True)
    >>> [(t.url, t.html) for t in get_items()]
    [('http://example.org/', '<html>\n</html>')]
    """
    if depth > max_depth_to_parse:
        return

    html = download_rate_limited(site_name, url, test)
    if html is None:
        return

    if should_save_html(url, needed):
        add_event(url=url, site_info=site_info, html=html, sources=[site_name])

    add_crawled_urls(site_name, url)
    soup = parse(html)

    # Find urls on page and elect them for processing
    for link in get_links(url, soup):
        if should_download_link(link, crawl_only, needed, lambda url: in_crawled_urls(site_name, url)):
            add_link(url=link,
                     site_info=site_info,
                     site_name=site_name,
                     crawl_only=crawl_only,
                     needed=needed,
                     depth=depth + 1,
                     test=test)


def get_links(url, soup):
    for tag in soup.find_all('a'):
        yield fix_link(tag.get('href'), url)


def download_rate_limited(site_name, url, test):
    return limit_rate(site_name, website_sleep_time, lambda: download(url, test=test))


def download(url, retries=0, test=False):
    if test:
        return test_html.get(url, test_html.get('404', None))
    try:
        response = urllib2.urlopen(url)
        print url
        return response.read()
    except Exception as e:
        if retries < 1:
            return download(url, retries + 1)
        print '`'


def limit_rate(name, min_time, func):
    """ Prevent flooding by limiting func
    >>> sleep_time = 0.2
    >>> _ = limit_rate('yo', sleep_time, lambda: time())
    >>> before = time()
    >>> after = limit_rate('yo', sleep_time, lambda: time())
    >>> (sleep_time - (after - before)) < (sleep_time / 2.0) # Close enough
    True
    """
    time_since_last_func = lambda: time() - website_lasthit_time.get(name, 0)
    while time_since_last_func() < min_time:
        sleep(in_range(min_time - time_since_last_func(), website_sleep_time, 0))
    website_lasthit_time[name] = time()
    return func()


def in_range(num, high, low):
    """
    >>> i = in_range
    >>> [i(10, 5, 0), i(-5, 10, 0), i(3, 5, 0)]
    [5, 0, 3]
    """
    return min(max(num, low), high)


# Async Functions
def add_site(site, test=False):
    pool.spawn(prepare, site, test)


add_link = lambda *args, **kwargs: pool.spawn(crawl, *args, **kwargs)

add_event = lambda **kwargs: events_retrieved.put(event(**kwargs))


def get_items():
    while True:
        events_retrieved.put(StopIteration)
        for item in events_retrieved:
            yield item
        pool.join(1)
        if len(pool) == 0:
            break

