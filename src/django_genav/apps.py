# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.apps import AppConfig
from django.apps import apps
from django.conf import settings as django_settings

from . import settings
from . import get_url_conf


class DefaultConfig(AppConfig):

    name = 'django_genav'

    def ready(self):
        self.navigation_autodiscover()

        urls_module = import_module(django_settings.ROOT_URLCONF)
        urls_module.urlpatterns = get_url_conf() + urls_module.urlpatterns


    @staticmethod
    def navigation_autodiscover():
        for app in apps.get_app_configs():
            for navigation_module_name in settings.AUTO_DISCOVER_NAMES:
                if module_has_submodule(app.module, navigation_module_name):
                    models_module_name = '%s.%s' % (app.name, navigation_module_name)
                    # Импортируем модуль, вся магия внутри во время создания типов
                    import_module(models_module_name)