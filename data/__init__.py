import os

path = ''
if '__file__' in globals():
    path = str(os.path.dirname(__file__)) + "/"


def get(directory, func):
    for root, subFolders, files in os.walk(path + directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, 'r') as f:
                yield func(f)


def get_yaml(directory):
    import yaml
    get_dict_merged = \
        lambda dict_list: reduce(lambda a, b: dict(a, **b), dict_list, {})
    return get_dict_merged(get(directory, lambda f: yaml.load(f)))


def get_categories(directory='categories'):
    return get_yaml(directory)


def get_site_list(directory='site_info'):
    """
    >>> len(get_site_list()) > 0
    True
    """
    site_list = get_yaml(directory)
    for site_name, site_info in site_list.items():
        site_info['name'] = site_name

    if site_list is {}:
        raise Exception("site_list is empty")
    return site_list
