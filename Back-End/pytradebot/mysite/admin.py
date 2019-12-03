from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import Usuario, CarteiraCriptomoeda, Trade, Estrategia
from .form import CustomUserChangeForm, CustomUserCreationForm

class UsuarioAdmin(UserAdmin):
    """
    Classe para representação de dados do modelo Usuario do banco de dados
    """

    # Campos para serem exibidos ao verificar o cadastro do usuário
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'cpf',
                                         'telefone', 'config_json')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Campos para serem exibidos ao cadastrar um usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'cpf',
                       'telefone', 'is_active', 'password1', 'password2')}
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('email', 'cpf', 'first_name', 'last_name', 'is_superuser')
    search_fields = ('email', 'cpf')
    ordering = ('email',)

class CarteiraAdmin(admin.ModelAdmin):
    """
    Classe para representação de dados do modelo Carteira do banco de dados
    """
    list_display = ('id', 'usuario')
    ordering = ['id']
    search_fields = ('id', 'usuario__email')
    list_per_page = 10

class TradeAdmin(admin.ModelAdmin):
    """
    Classe para representação de dados do modelo Trade do banco de dados
    """
    list_display = ('id', 'user')
    ordering = ['id']
    search_fields = ('id', 'user__email')
    list_per_page = 10

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(CarteiraCriptomoeda, CarteiraAdmin)
admin.site.register(Trade, TradeAdmin)
admin.site.register(Estrategia)
