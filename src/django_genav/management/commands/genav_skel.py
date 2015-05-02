# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.apps import apps

class Command(BaseCommand):

    args = 'module'
    # help = 'Creates initial file content for django module'

    def handle(self, module_name, **kwargs):
        pass