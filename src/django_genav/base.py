import re

from collections import OrderedDict

from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse as dango_reverse
from django_genav.utils import dict_copy

from . import utils
from . import settings


__all__ = \
    [ 'NavigationModel'
    , 'get_url_conf'
    , 'print_url_conf'
    , 'reverse'
    ]


class NavigationManager(object):

    view = None
    view_class = None
    navigation_class = None

    _patterns_cache = dict()


    def __repr__(self):
        return self._repr()

    def _repr(self, indent=0):
        result = (' ' * 4 * indent) + self.name + '\n'
        descendants = self.get_descendants() or {}
        for view_class, children_view_class in descendants.iteritems():
            result += view_class.nav._repr(indent=indent+1)
        return result

    def __init__(self, view, view_class, navigation_class):
        self.view = view
        self.view_class = view_class
        self.navigation_class = navigation_class

    def meta(self, name, default=None):
        return getattr(self.navigation_class, name, None) or default

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
    def parent_view(self):
        result = self.meta('parent')
        if type(result) is str:
            view_path = result.split('.')[:2]
            if len(view_path) == 2:
                result = utils.get_view(*view_path)
            else:
                return None
        return result

    @property
    def parent(self):
        return self.get_parent()

    def get_parent(self):
        if self.parent_view:
            return getattr(self.parent_view, settings.VIEW_NAVIGATION_ATTRIBUTE, None)
        return None

    @property
    def ancestors(self):
        return self.get_ancestors()

    def get_ancestors(self):
        result = []
        parent = self.parent
        while parent:
            result.append(parent)
            parent = parent.parent
        return result

    @property
    def descendants(self):
        return self.get_descendants()

    def get_descendants(self):
        global _registry
        result = OrderedDict()
        children = self.get_children()
        if children:
            for view_class in children:
                result[view_class] = view_class.nav.get_children()
        else:
            return None
        return result

    @property
    def children(self):
        return self.get_children()

    def get_children(self):
        global _registry
        result = []
        for name, view_class in _registry.items():
            if utils.getattr_deep(view_class, 'nav', 'parent', 'name') == self.name:
                result.append(view_class)
        return sorted(result, key=lambda v: v.nav.name)

    @property
    def args_all(self):
        result = []
        for url_pattern in self.url_patterns:
            result.append(self.get_compiled_pattern(url_pattern).groupindex.keys())
        return result

    @property
    def url_patterns(self):
        result = []
        parent = self.parent
        url_exclude_with_args = self.meta('url_exclude_with_args')

        if not parent:
            url = self.meta('url')
            if type(url) is str:
                raise ValueError\
                    ('Strings are forbidden for url attribute maybe you forgot comma in brackets? url = ("%s", )' % url)
            result = self.meta('url')[:]
        else:

            for parent_url_pattern in parent.url_patterns:
                for self_url_pattern in self.meta('url'):
                    # pass filtered by ars url patterns
                    if url_exclude_with_args:
                        all_keys = set\
                            ( self.get_compiled_pattern(parent_url_pattern.rstrip('$') + self_url_pattern).groupindex.keys()
                            )
                        if all_keys & set(url_exclude_with_args):
                            continue

                    # add from root
                    if self_url_pattern.startswith('/'):
                        result.append(self_url_pattern)

                    # append to parent's ur;
                    else:
                        result.append(parent_url_pattern.rstrip('$') + self_url_pattern)

        return map(self.prepare_url_pattern, utils.unique(result))

    def prepare_url_pattern(self, url_pattern):
        url_pattern = url_pattern.lstrip('/')
        url_pattern = '^' + url_pattern.lstrip('^')
        url_pattern = url_pattern.rstrip('$') + '$'
        return url_pattern

    def get_compiled_pattern(self, url_pattern):
        return self._patterns_cache.get(url_pattern) or \
            self._patterns_cache.setdefault(url_pattern, re.compile(url_pattern))

    def get_url_by_args(self, *args):
        args = set(args)
        match = list((None, None, 0))
        for url_pattern in self.url_patterns:
            url_pattern_args = set(self.get_compiled_pattern(url_pattern).groupindex.keys())
            if url_pattern_args <= args:
                match.append((url_pattern, url_pattern_args, len(url_pattern_args & args)))
        url_pattern, url_pattern_args, score = max(match, key=lambda v: v[2])
        return url_pattern, url_pattern_args

    def reverse(self, name_or_view=None, kwargs=None, exclude=None):
        """
        View.nav.reverse(kwargs={...})
            - reverse through itself with given kwargs

        View().nav.reverse()
            - reverse self using it self kwargs

        View().nav.reverse(kwargs={...})
            - reverse self using it self kwargs merging with given kwargs

        View().nav.reverse('another.view.name')
            - reverse another view using it self kwargs

        View().nav.reverse('another.view.name', kwargs={...})
            - reverse another view using it self kwargs merging with given kwargs
        """
        if name_or_view and not self.view:
            raise NotImplementedError('')

        # Merging kwargs
        kwargs = kwargs or {}
        view_kwargs = dict_copy(getattr(self.view, 'kwargs', None) or {})
        view_kwargs.update(kwargs)
        kwargs = view_kwargs

        if exclude:
            for key in exclude:
                kwargs.pop(key, None)

        # Resolve view name
        view_class = _registry.get(name_or_view) or name_or_view or self
        manager = getattr(view_class, settings.VIEW_NAVIGATION_ATTRIBUTE, None) or self
        name = getattr(manager, 'name', None) or self.name

        # Trying to guess best kwarg combination
        requested_args = set(kwargs.keys())
        best_match = set()
        for arg_set in manager.args_all:
            arg_set = set(arg_set)
            if arg_set <= requested_args:
                matched_args = requested_args & arg_set
                if len(matched_args) > len(best_match):
                    best_match = matched_args
        kwargs = {k: v for k, v in kwargs.iteritems() if k in best_match}
        return dango_reverse(name, kwargs=kwargs)

    def back(self):
        if not self.view:
            raise ValueError('View instance is required for this operation')

        # if view implements it's own method to resolve back_url
        get_back_url = getattr(self.view, 'get_back_url', None)
        if get_back_url:
            return get_back_url()

        # if Navigation class implements get_back
        get_back = self.meta('back')
        if callable(get_back):
            result = get_back(self.view)
            if result is not None:
                return result

        # Try to resolve with given data
        if self.parent:
            return self.parent.reverse(kwargs=self.view.kwargs)

        # Or there are no back_url at all
        return None

    @property
    def url_conf(self):
        result = []
        for url_pattern in self.url_patterns:
            view = self.view_class
            if hasattr(view, 'as_view'):
                view = view.as_view()
            result.append(url(url_pattern, view, name=self.name))
        return result


class NavigationProxy(object):

    navigation_class = None

    def __init__(self, navigation_class):
        self.navigation_class = navigation_class

    def __get__(self, view, view_class=None):
        if view is None:
            return NavigationManager(None, view_class, self.navigation_class)
        res = view.__dict__[settings.VIEW_NAVIGATION_ATTRIBUTE] = NavigationManager(view, view_class, self.navigation_class)
        return res


_registry = dict()


class NavigationModelMeta(type):

    def __new__(mcs, name, bases, attributes):
        global _registry
        result = super(NavigationModelMeta, mcs).__new__(mcs, name, bases, attributes)
        if object not in bases and NavigationModel in bases:
            view_class = attributes.get('view') or None
            if view_class is None:
                raise NotImplementedError\
                    ('Navigation view attribute must be defined')

            if not type(view_class) is type:
                raise ValueError('It is senselessly to make descriptor work with instance of "%s" not type objects' % view_class)

            setattr(view_class, settings.VIEW_NAVIGATION_ATTRIBUTE, NavigationProxy(result))

            name = getattr(view_class, settings.VIEW_NAVIGATION_ATTRIBUTE).name
            registry_view = _registry.setdefault(name, view_class)
            if registry_view != view_class:
                raise ValueError\
                    ('View name "%s" for "%s" already registered, choose another.' % (name, view_class))
        return result


class NavigationModel(object):
    __metaclass__ = NavigationModelMeta


def get_url_conf():
    result = ['', ]
    for name, item in _registry.iteritems():
        manager = getattr(item, settings.VIEW_NAVIGATION_ATTRIBUTE, None)
        if manager:
            result.extend(manager.url_conf)
    return patterns(*result)


def print_url_conf():
    for name, view_class in sorted(_registry.iteritems(), key=lambda v: v[0]):
        if view_class.nav.parent is None:
            print view_class.nav


def reverse(name_or_view_class, kwargs=None):
    kwargs = kwargs or {}
    view_class = _registry.get(name_or_view_class) or name_or_view_class
    manager = getattr(view_class, settings.VIEW_NAVIGATION_ATTRIBUTE, None)
    if not manager:
        return dango_reverse(name_or_view_class, kwargs=kwargs)
    return manager.reverse(kwargs=kwargs)
