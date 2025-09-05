from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another substring.
    Usage: {{ value|replace:"old_string,new_string" }}
    """
    if isinstance(value, str) and isinstance(arg, str):
        try:
            old_string, new_string = arg.split(',')
            return value.replace(old_string, new_string)
        except ValueError:
            # Handle cases where arg is not in "old,new" format
            return value
    return value