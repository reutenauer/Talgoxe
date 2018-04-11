from django import template
register = template.Library()

def romanlower(value):
    """Returns a for 1, b for 2, etc."""
    return chr(value + 96)

register.filter('romanlower', romanlower)
