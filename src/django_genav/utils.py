from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
import re

from django.apps import apps


__all__ = \
    [ 'camel_to_under'
    , 'dict_copy'
    , 'get_view'
    ]


CAMEL_TO_UNDER_PATTERN_1 = re.compile(r'(.)([A-Z][a-z]+)')
CAMEL_TO_UNDER_PATTERN_2 = re.compile(r'([a-z0-9])([A-Z])')


def unique(n):
    u = set()
    return [i for i in n if i not in u and not u.add(i)]


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
        if module_has_submodule(app.module, 'views'):
            models_module_name = '%s.%s' % (app.name, 'views')
            views = import_module(models_module_name)
            return getattr(views, view_name)
    except (ImportError, AttributeError):
        # Fail silent if views.py does not exist
        pass

    return None


def getattr_deep(obj, *attrs, **kwargs):
    default = kwargs.get('default') or None
    for attr in attrs:
        try:
            obj = getattr(obj, attr)
        except AttributeError:
            return default
    return obj
