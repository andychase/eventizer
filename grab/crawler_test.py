import unittest
from collections import namedtuple
from common import event
from crawler import prepare, get_items, crawl
import crawler

crawler.add_link = lambda *args, **kwargs: crawl(*args, **kwargs)
crawler.website_sleep_time = 0


html = lambda body: "<html><head></head><body>{}</body></html>".format(body)

test_site_info = namedtuple(
    'test_site_info',
    'name baseurl urlnosaveregex urlregex html_hints test_html test_answer'
)

tests = [

    test_site_info(
        name='test1',
        baseurl='http://test1/',
        test_html={
            'http://test1/': html("<a href='/nosave'></a>"),
            'http://test1/nosave': html("<a href='/event'></a>"),
            'http://test1/event': html("<span>answer</span>"),
        },
        urlnosaveregex='/nosave',
        urlregex='/event',
        html_hints={'name': 'span'},
        test_answer=event(html=html('<span>answer</span>'))
    ),
    test_site_info(
        name='test2',
        baseurl='http://test2/',
        test_html={
            'http://test2/': html("<a href='/nosave'></a>"),
            'http://test2/nosave': html("<a href='http://test2/event'></a>"),
            'http://test2/event': html("<span>answer</span>"),
        },
        urlnosaveregex='/nosave',
        urlregex='/event',
        html_hints={'name': 'span'},
        test_answer=event(html=html('<span>answer</span>'))
    ),
    test_site_info(
        name='ww_test',
        baseurl='http://www.com/portland/e.h',
        test_html={
            'http://www.com/portland/e.h':
                html('<a href="event-169055-miguel_gutierrez_and_the_powerful_people.html"></a>'),
            'http://www.com/portland/event-169055-miguel_gutierrez_and_the_powerful_people.html':
                html("<span>answer</span>"),
        },
        urlnosaveregex='/nosave',
        urlregex='/portland/event-[0-9]+-.+\.html',
        html_hints={'name': 'span'},
        test_answer=event(html=html('<span>answer</span>'))
    )
]


class CrawlerTest(unittest.TestCase):

    def test_crawling(self):
        for test in tests:
            crawler.test_html = test.test_html
            prepare(test._asdict(), test=True)
            result = list(get_items())
            self.assertNotEqual([], result)
            self.assertEquals(result[0].html, test.test_answer.html)
