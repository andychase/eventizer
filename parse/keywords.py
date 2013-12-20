def merge_words(words, desc):
    """
    >>> list(merge_words(["Wow", "Yo", "Yo"], "Wow and Yo Yo"))
    ['Wow', 'Yo Yo']
    """
    size = len(words)
    skipNext = False
    for i, word in enumerate(words):
        if skipNext:
            skipNext = False
            continue
        if i + 1 < size:
            comb = word + " " + words[i + 1]
            if desc.find(comb) != -1:
                yield comb
                skipNext = True
            else:
                yield word
        else:
            yield word


def capitalized(letter):
    return letter.lower() == letter


def get_keywords(text):
    """
    >>> from collections import namedtuple
    >>> event = namedtuple('event', 'description keywords')
    >>> def put(i): print i
    >>> get_keywords("Go and see Vince Vincent")
    ['Go', 'Vince Vincent']
    >>> get_keywords("GO AND SEE VINCE VINCENT")
    []
    """
    words = text.split(" ")
    # Get words longer than one letter
    words = filter(lambda word: len(word) > 1, words)
    # Filter not capitalized words
    words = filter(lambda word: not capitalized(word[0]), words)
    # Remove ALL CAPS words
    words = filter(lambda word: capitalized(word[1]), words)
    # Merge words that are adjacent
    words = list(merge_words(words, text))
    return words