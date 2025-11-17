from django import template

register = template.Library()

@register.filter
def currency(value):

    
    try:
        if value:
            value = float(value)
        else:
            value = 0
        formatted = f"R$ {value:,.2f}"

        formatted = formatted.replace(',','X').replace('.',',').replace('X','.')
        return formatted
    
    except (ValueError, TypeError):
        return value