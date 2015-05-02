import re

from django.apps import apps


__all__ = \
    [ 'camel_to_under'
    , 'dict_copy'
    , 'get_view'
    ]


CAMEL_TO_UNDER_PATTERN_1 = re.compile(r'(.)([A-Z][a-z]+)')
CAMEL_TO_UNDER_PATTERN_2 = re.compile(r'([a-z0-9])([A-Z])')


def camel_to_under(name):
    return \
        CAMEL_TO_UNDER_PATTERN_2.sub\
            ( r'\1_\2'
            , CAMEL_TO_UNDER_PATTERN_1.sub(r'\1_\2', name)
            ).lower()


def dict_copy(d):
    """
    much, much faster than deepcopy, for a dict of the simple python types.
    """
    out = d.copy()
    for k, v in d.iteritems():
        if isinstance(v, dict):
            out[k] = dict_copy(v)
        elif isinstance(v, list):
            out[k] = v[:]
    return out


def get_view(app_label, view_name):
    try:
        app = apps.get_app_config(app_label)
    except LookupError:
        return None

    try:
        return getattr(app.module.views, view_name)
    except AttributeError:
        return None

