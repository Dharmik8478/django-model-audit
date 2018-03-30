import ast

from django import template
from django.utils.safestring import mark_safe
from django.template import Template, Context
from django.conf import settings

register = template.Library()


@register.filter(needs_autoescape=True)
def render(text, text_type, autoescape=True):
    try:
        text = text.decode()
    except AttributeError:
        text = text.tobytes().decode()
    if text == 'None' or not text:
        template = '-'
    elif text_type == 'ManyToMany':
        text = ast.literal_eval(text)
        template = '<ul style="text-align:left;"><li>'+'</li><li>'.join(text)+'</li></ul>'
    elif text_type == 'File' or text_type=='ImageFieldFile' or     text_type=='FilePath':
        template = '<a href="'+settings.MEDIA_URL+text+'">Download</a>'
    elif text_type == 'Boolean' or text_type=='NullBoolean':
        text = ast.literal_eval(text)
        template = '&#10004;' if text else '&#10008;'
    else:
        template = text
    return Template(template).render(Context({}))

full_name = {'I': 'Insert', 'U': 'Update', 'D': 'Delete'}

@register.filter()
def get_full_name(value):
    return full_name.get(value)

