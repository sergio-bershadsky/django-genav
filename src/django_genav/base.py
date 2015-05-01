import re

from . import utils
from . import settings


class NavigationManager(object):

    view = None
    view_class = None
    navigation_class = None

    _patterns_cache = dict()

    def __init__(self, view, view_class, navigation_class):
        self.view = view
        self.view_class = view_class
        self.navigation_class = navigation_class

    def meta(self, name, default=None):
        return getattr(self.navigation_class, name, None) or default

    @property
    def id(self):
        ancestors = [parent.name for parent in self.ancestors]
        ancestors.reverse()
        return '.'.join(ancestors + [self.name])

    @property
    def name(self):
        return self.meta('name') or (utils.camel_to_under(self.view_class.__name__).replace('_view', ''))

    @property
    def args(self):
        result = []
        for url_pattern in self.meta('url', []):
            result.append(tuple(self.get_compiled_pattern(url_pattern).groupindex.keys()))
        return result

    @property
    def parent(self):
        parent = self.meta('parent')
        if parent:
            return self.meta('parent').nav
        return None

    @property
    def ancestors(self):
        result = list()
        parent = self.parent
        while parent:
            result.append(parent)
            parent = parent.parent
        return result

    @property
    def args_all(self):
        result = []
        parent = self.parent
        if not parent:
            return self.args
        else:
            parent_args = parent.args_all
            for parent_arg in parent_args:
                if self.args:
                    for self_arg in self.args:
                        result.append(parent_arg + self_arg)
                else:
                    return parent_args
        return result

    @property
    def url_patterns(self):
        result = []
        parent = self.parent
        url_exclude_with_args = self.meta('url_exclude_with_args')

        if not parent:
            result = self.meta('url')[:]
        else:
            for parent_url_pattern in parent.url_patterns:
                for self_url_pattern in self.meta('url'):
                    if url_exclude_with_args:
                        all_keys = set\
                            ( self.get_compiled_pattern(parent_url_pattern).groupindex.keys() +
                              self.get_compiled_pattern(self_url_pattern).groupindex.keys()
                            )
                        if all_keys & set(url_exclude_with_args):
                            continue
                    if self_url_pattern.startswith('/'):
                        result.append(self_url_pattern)
                    else:
                        result.append(parent_url_pattern + self_url_pattern)
        return result

    def get_compiled_pattern(self, url_pattern):
        return self._patterns_cache.get(url_pattern) or \
            self._patterns_cache.setdefault(url_pattern, re.compile(url_pattern))

    def get_url_by_args(self, *args):
        args = set(args)
        match = list()
        for url_pattern in self.url_patterns:
            url_pattern_args = set(self.get_compiled_pattern(url_pattern).groupindex.keys())
            if url_pattern_args <= args:
                match.append((url_pattern, url_pattern_args, len(url_pattern_args & args)))
        best_match = max(match, key=lambda v: v[2])
        return best_match[0], best_match[1]

    def url_reverse(self, **kwargs):
        requested_args = set(kwargs.keys())
        best_match = set()
        for arg_set in self.args_all:
            arg_set = set(arg_set)
            if arg_set <= requested_args:
                matched_args = requested_args & arg_set
                if len(matched_args) > len(best_match):
                    best_match = matched_args
        return {k: v for k, v in kwargs.iteritems() if k in best_match}


class NavigationProxy(object):

    navigation_class = None

    def __init__(self, navigation_class):
        self.navigation_class = navigation_class

    def __get__(self, view, view_class=None):
        if view is None:
            return NavigationManager(None, view_class, self.navigation_class)
        res = view.__dict__[settings.VIEW_NAVIGATION_ATTRIBUTE] = NavigationManager(view, view_class, self.navigation_class)
        return res


class NavigationModelMeta(type):

    _registry = dict()

    def __new__(mcs, name, bases, attributes):
        result = super(NavigationModelMeta, mcs).__new__(mcs, name, bases, attributes)
        if object not in bases and NavigationModel in bases:
            view = attributes.get('view') or None
            if view is None:
                raise NotImplementedError\
                    ('Navigation view attribute must be defined')
            setattr(view, settings.VIEW_NAVIGATION_ATTRIBUTE, NavigationProxy(result))
            name = view.nav.name
            registry_view = mcs._registry.setdefault(name, view)
            if registry_view != view:
                raise ValueError\
                    ('View name "%s" for "%s" already registered, choose another.' % (name, view))
        return result


class NavigationModel(object):
    __metaclass__ = NavigationModelMeta