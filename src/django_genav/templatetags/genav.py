from django import template


from ..base import reverse
from ..utils import dict_copy


register = template.Library()


@register.simple_tag(takes_context=True)
def url(context, name_or_view=None, *args, **kwargs):
    as_name = kwargs.get('as')

    if type(name_or_view) is dict:
        kwargs = name_or_view
    context_view = context.get('view')
    view = name_or_view or context_view
    if not view:
        raise ValueError('View does not provided')

    if not kwargs and len(args) == 1 and type(args[0]) is dict:
        kwargs = args[0]

    merged_kwargs = getattr(context_view, 'kwargs', None) or {}
    if merged_kwargs:
        merged_kwargs = dict_copy(merged_kwargs)
    merged_kwargs.update(kwargs)

    result = reverse(view, **merged_kwargs)
    if as_name:
        context.update({as_name: result})
        return ''
    return result


@register.assignment_tag(takes_context=True)
def url_as(context, name_or_view=None, *args, **kwargs):
    return url(context, name_or_view, *args, **kwargs)