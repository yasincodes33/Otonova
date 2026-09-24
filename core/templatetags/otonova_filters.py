from django import template

register = template.Library()


@register.filter
def para(value):
    """3200000 → '3.200.000'"""
    try:
        return f"{int(float(value)):,}".replace(",", ".")
    except (TypeError, ValueError):
        return value
