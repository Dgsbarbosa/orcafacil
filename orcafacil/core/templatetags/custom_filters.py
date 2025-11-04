from django import template

register = template.Library()

@register.filter
def splitCode(value, delimiter="/"):
    if not value:
        return ""
    return value.split(delimiter)[0]

