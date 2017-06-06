from django import template

register = template.Library()


@register.filter
def to_pc_url(value):
    return value.replace("/m.", "/")
