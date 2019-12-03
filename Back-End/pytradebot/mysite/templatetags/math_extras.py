from django import template

register = template.Library()

@register.filter(name='multiplicar')
def multiplicar(n_1, n_2):
    """
    Filtro de template para realizar a multiplicação dos números.
    """
    return float(n_1) * float(n_2)

@register.filter(name='dividir')
def dividir(n_1, n_2):
    """
    Filtro de template para realizar a divisão dos números.
    """
    return float(n_1) / float(n_2)

@register.filter(name='somar')
def somar(n_1, n_2):
    """
    Filtro de template para realizar a soma dos números.
    """
    return float(n_1) + float(n_2)

@register.filter(name='subtrair')
def subtrair(n_1, n_2):
    """
    Filtro de template para realizar a subtração dos números.
    """
    return float(n_1) - float(n_2)
