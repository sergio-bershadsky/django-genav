from django.conf import settings


__PREFIX__ = 'GENAV_'


VIEW_NAVIGATION_ATTRIBUTE = str(getattr(settings, __PREFIX__ + 'VIEW_NAVIGATION_ATTRIBUTE', None) or 'nav')
AUTO_DISCOVER_NAMES = tuple(getattr(settings, __PREFIX__ + 'AUTO_DISCOVER_NAMES', None) or ('navigation', ))