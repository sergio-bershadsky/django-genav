from django import template
from django.core.urlresolvers import reverse as django_reverse

from ..base import reverse
from ..utils import dict_copy


register = template.Library()


@register.simple_tag(takes_context=True)
def url_strict(context, name, **kwargs):
    return django_reverse(name, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def url(context, name_or_view=None, **kwargs):
    as_name = kwargs.get('as')

    if type(name_or_view) is dict:
        kwargs = name_or_view
    context_view = context.get('view')
    view = name_or_view or context_view
    if not view:
        raise ValueError('View does not provided')

    merged_kwargs = getattr(context_view, 'kwargs', None) or {}
    if merged_kwargs:
        merged_kwargs = dict_copy(merged_kwargs)
    merged_kwargs.update(kwargs)

    result = reverse(view, kwargs=merged_kwargs)
    if as_name:
        context.update({as_name: result})
        return ''
    return result


@register.assignment_tag(takes_context=True)
def url_as(context, name_or_view=None, *args, **kwargs):
    return url(context, name_or_view, *args, **kwargs)