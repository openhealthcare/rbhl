import collections

def _remove_key(d, key):
    """
    Remove the given key from the given dictionary recursively
    """
    for k, v in d.items():
        if k == key:
            continue

        if isinstance(v, collections.Mapping):
            yield k, dict(_remove_key(v, key))
        elif isinstance(v, list):
            yield k, [dict(_remove_key(x, key)) for x in v]
        else:
            yield k, v


def remove_keys(d, *keys):
    """
    Recursively remove many keys from a dictionary
    """
    if len(keys) == 0:
        return d
    if len(keys) == 1:
        return dict(_remove_key(d, keys[0]))
    return remove_keys(dict(remove_keys(d, keys[0])), *keys[1:])


def remove_empty_lists(d):
    """
    Recursively remove any keys which are an empty list from a dictionary
    """
    if isinstance(d, collections.Mapping):
        return {k: remove_empty_lists(v) for k, v in d.items() if v != []}
    if isinstance(d, list):
        return [remove_empty_lists(i) for i in d if i != []]
    else:
        return d
