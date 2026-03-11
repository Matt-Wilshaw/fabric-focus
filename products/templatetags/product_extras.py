from django import template

register = template.Library()


@register.filter
def pretty_category(value):
    """Render category slugs in a user-friendly way."""
    if value is None:
        return ""
    text = str(value).replace("_", " ").replace("-", " ").strip()
    return " ".join(word.capitalize() for word in text.split())
