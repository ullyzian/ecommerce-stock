from django import template
from core.models import Category

register = template.Library()


@register.filter
def categories(value):
    return Category.objects.all()
