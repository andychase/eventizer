from db import get_keyword_count, insert_keywords


def get_uniqueness(keywords, name):
    """ Search for things that make this event popular
        and pass them all forward
    //>>> from collections import namedtuple
    //>>> def put(i): print i
    //>>> main(namedtuple('event', 'keywords scores')([], {}),put)
    event(keywords=[], scores={'uniqueness': 1000})
    """
    # Insert our keywords
    return 0
    if True:
        raise Exception("Not completed yet")
    insert_keywords(keywords, name)

    # Get Keyword popularity
    keyword_score = [get_keyword_count(keyword) for keyword in keywords]
    return 1000 + (1000 * len(keywords)) - sum(keyword_score)