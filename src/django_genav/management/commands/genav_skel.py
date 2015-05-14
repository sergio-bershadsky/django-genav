# -*- coding: utf-8 -*-
import re

from importlib import import_module
from django.core.management import BaseCommand
from django.apps import apps
from django.utils.module_loading import module_has_submodule
from django.views.generic import View
from django_genav import utils


class Command(BaseCommand):

    args = 'app_name class_name_pattern'

    TEMPLATE = """# -*- coding: utf-8 -*-
from django_genav import NavigationModel

from . import views


{all_str}


{classes_str}
"""

    CLASS_TEMPLATE = r"""
class {class_name}(NavigationModel):
    url = \
        ( ""
        , )
    view = views.{view_class_name}
    parent = ""
    name = "{view_name}"

"""

    def handle(self, app_name, class_name_pattern=None, **kwargs):
        if class_name_pattern:
            class_name_pattern = re.compile(class_name_pattern)

        view_module = None
        for app in apps.get_app_configs():
            if app.name == app_name:
                if module_has_submodule(app.module, 'views'):
                    models_module_name = '%s.%s' % (app.name, 'views')
                    # Импортируем модуль, вся магия внутри во время создания типов
                    view_module = import_module(models_module_name)
                    break

        if view_module:
            views = dict()
            for member_name in sorted(dir(view_module)):
                if not member_name.startswith('_'):
                    member = getattr(view_module, member_name)
                    if type(member) is type and issubclass(member, View) and member is not View:
                        view_class_path = '.'.join([member.__module__, member.__name__])
                        views[view_class_path] = member

            if views:
                classes_str = ''
                all_str = []
                for view_class_path, view_class in sorted(views.items()):
                    view_class_name = view_class.__name__

                    if class_name_pattern and not class_name_pattern.match(view_class_name):
                        continue

                    class_name = view_name_for_dotted = view_class_name
                    if class_name.endswith('View'):
                        class_name = view_name_for_dotted = class_name[:-4]

                    view_name = utils.camel_to_under(view_name_for_dotted).replace('_', '.')

                    class_name += 'Navigation'
                    all_str.append(class_name)
                    classes_str += self.CLASS_TEMPLATE.format(**locals())

                tab = '    '
                all_str = '__all__ = \\\n{tab}( %s\n{tab})' % ('\n{tab}, '.join(map(lambda v: '"%s"' % v, all_str)).lstrip('\n, '))
                all_str = all_str.format(**locals())

                result = self.TEMPLATE.format(**locals()).strip("\n")
                print result