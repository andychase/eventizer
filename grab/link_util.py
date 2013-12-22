#!python
# coding=utf-8
from __future__ import unicode_literals
import urlparse

valid_scheme = lambda scheme: scheme in ["http", "https"]


def should_save_html(url, needed):
    return bool(needed.match(urlparse.urlparse(url).path))


def should_download_link(link, crawl_only, needed, in_crawled_urls):
    r"""
    >>> import re
    >>> r = lambda regex: re.compile(regex)
    >>> should_download_link('http://example.org/test', r('/test'), r('asdfasfd'), lambda _: False)
    True
    >>> should_download_link('http://example.org/d/test', r('/d/test'), r('asdfasfd'), lambda _: False)
    True
    """
    if link is None:
        return False
    else:
        link_parts = urlparse.urlparse(link)
        link = link_parts.scheme + "://" + link_parts.netloc + link_parts.path
        matching = bool(crawl_only.match(link_parts.path) or needed.match(link_parts.path))
        return matching and valid_scheme(link_parts.scheme) and not in_crawled_urls(link)


def fix_link(link, url):
    """
    >>> fix_link('/yo', 'http://test.com')
    u'http://test.com/yo'
    >>> fix_link('yo', 'http://test.com/ext/ext.html')
    u'http://test.com/ext/yo'
    >>> fix_link('yo', 'http://test.com/cool.html')
    u'http://test.com/yo'
    >>> fix_link('yo#test', 'http://test.com/cool.html')
    u'http://test.com/yo'
    >>> fix_link('yo?where=4#test', 'http://test.com/cool.html')
    u'http://test.com/yo?where=4'
    >>> fix_link('yoܩ', 'http://example.com') == u'http://example.com/yoܩ'
    True
    """
    fixed_url = urlparse.urljoin(url, link)
    parsed_url = urlparse.urlparse(fixed_url)
    if parsed_url.query:
        parsed_url = parsed_url._replace(query=u'?'+parsed_url.query)
    combined_url = u"{scheme}://{netloc}{path}{query}".format(**parsed_url._asdict())
    return combined_url
