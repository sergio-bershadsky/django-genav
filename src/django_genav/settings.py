from django.conf import settings


__PREFIX__ = 'GENAV_'


VIEW_NAVIGATION_ATTRIBUTE = getattr(settings, __PREFIX__ + 'VIEW_NAVIGATION_ATTRIBUTE') or 'nav'