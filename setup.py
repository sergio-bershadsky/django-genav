#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages


setup\
    ( name='django_genav'
    , version='1.0'
    , description='Plugin for organazing Django views as hierarchical tree, generating menus, breadcrumbs, traversing and etc'
    , author='Sergey Nikitin'
    , author_email='nikitinsm@gmail.com'
    , url='https://github.com/nikitinsm/django-genav'
    , packages = find_packages('src')
    , package_dir = {'': 'src'}
    , include_package_data = True
    # , install_requires =
    #   [ "django"
    #   , ]
    )