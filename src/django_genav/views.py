

class NavigationProxy(object):

    def __init__(self, navigation_class):
        self._navigation_class = navigation_class

    def __get__(self, instance, owner):
        return Navigation(instance, owner)


class Navigation(object):

    _view = None
    _view_cls = None

    def __init__(self, view=None, view_cls=None):
        self._view = view
        self._view_cls = view_cls

    @property
    def label(self):
        return self.get_label()

    def get_label(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def parent_url(self):
        return self.get_parent_url()

    def get_parent_url(self, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def get_url_conf(cls):
        pass


class BaseNavigation(object):

    def get_label(self, *args, **kwargs):
        raise NotImplementedError()

    def get_parent_url(self, *args, **kwargs):
        raise NotImplementedError()


class GenericNavigationViewMixin(object):

    nav = NavigationProxy(BaseNavigation)