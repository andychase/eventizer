def build_category_fixer(category_list):
    """
    >>> build_category_fixer({'concert': ['mus', 'listen']})('listen')
    'concert'
    """
    # Create an inverse index for quick lookups
    category_index = {}
    for correct_name, alternatives in category_list.items():
        for alternative in alternatives:
            category_index[alternative] = correct_name
    return lambda category_name: category_index.get(category_name, category_name)