from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """
    Filtro de template para realizar a multiplicação do valor com o argumento dado.
    """
    return value * arg
