from django import template

register = template.Library()

@register.filter
def sum_product(items, attr):
    return sum(getattr(item.product, attr) * item.quantity for item in items)

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtracts arg from value."""
    try:
        return value - arg
    except Exception as e:
        return ''