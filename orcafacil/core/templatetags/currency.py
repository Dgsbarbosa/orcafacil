from django import template

register = template.Library()

@register.filter
def currency(value):
    try:
        value = float(value)
        formatted = f"R$ {value:,.2f}"

        formatted = formatted.replace(',','X').replace('.',',').replace('X','.')
        return formatted
    
    except (ValueError, TypeError):
        return value