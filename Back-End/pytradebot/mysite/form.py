from django.forms import widgets, ModelForm, Form
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, \
                                        PasswordChangeForm, UserCreationForm, UserChangeForm
from localflavor.br.validators import BRCPFValidator
from parsley.decorators import parsleyfy
from .models import Usuario, CarteiraCriptomoeda

class CustomUserCreationForm(UserCreationForm):
    """
    Classe do formulário para criação de usuário pelo Django Admin
    """

    class Meta:
        model = Usuario
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):
    """
    Classe do formulário para alterar usuário pelo Django Admin
    """

    class Meta:
        model = Usuario
        fields = '__all__'

@parsleyfy
class ChangePasswordForm(PasswordChangeForm):
    """
    Classe do formulário para alterar senha quando o usuário está logado
    """
    # Classe de Metadados
    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']

        parsley_extras = {
            'new_password1': {
                'remote': reverse_lazy('parsley-validar-senha'),
                'remote-message': "Digite uma senha com números e caracteres"
            },
            'new_password2': {
                'equalto': "new_password1",
                'error-message': "As senhas digitadas não são iguais",
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'reset-form'
    scope_prefix = 'dados_reset'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    # Senha atual
    old_password = forms.CharField(
        label='Senha atual',
        max_length=16,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'placeholder': "Senha atual",
            'autocomplete': "off",
        })
    )

    # Nova senha
    new_password1 = forms.CharField(
        label='Nova senha',
        max_length=16,
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "Senha",
            'autocomplete': "off",
        }),
        error_messages={
            'min_length': "O tamanho da senha é muito curta.",
        }
    )

    # Confirmar a nova senha
    new_password2 = forms.CharField(
        label='Confirmar a nova senha',
        max_length=16,
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Senha",
            'autocomplete': "off",
        }),
        help_text='Digite a sua senha novamente',
        error_messages={
            'min_length': "O tamanho da senha é muito curta.",
        }
    )

    initial = {
        'old_password': '',
        'new_password1': '',
        'new_password2': '',
    }

@parsleyfy
class ResetForm(SetPasswordForm):
    """
    Classe do formulário para alterar senha
    """
    # Classe de Metadados
    class Meta:
        fields = ['new_password1', 'new_password2']

        parsley_extras = {
            'new_password1': {
                'remote': reverse_lazy('parsley-validar-senha'),
                'remote-message': "Digite uma senha com números e caracteres"
            },
            'new_password2': {
                'equalto': "new_password1",
                'error-message': "As senhas digitadas não são iguais",
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(ResetForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'reset-form'
    scope_prefix = 'dados_reset'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    # Senha
    new_password1 = forms.CharField(
        label='Senha',
        max_length=16,
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "Senha",
            'autocomplete': "off",
        }),
        error_messages={
            'min_length': "O tamanho da senha é muito curta.",
        }
    )

    # Confirmar Senha
    new_password2 = forms.CharField(
        label='Reinsira sua senha',
        max_length=16,
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Senha",
            'autocomplete': "off",
        }),
        help_text='Digite a sua senha novamente',
        error_messages={
            'min_length': "O tamanho da senha é muito curta.",
        }
    )

    initial = {
        'new_password1': '',
        'new_password2': '',
    }

@parsleyfy
class CheckResetForm(PasswordResetForm):
    """
    Classe do formulário para verificar redifinição de senha por email
    """

    # Classe de Metadados
    class Meta:
        fields = ['email']

        parsley_extras = {
            'email': {
                'remote': reverse_lazy('parsley-verificar-email'),
                'remote-message': "O Email digitado não está cadastrado no sistema."
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(CheckResetForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'reset-form'
    scope_prefix = 'dados_reset'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    # Email
    email = forms.EmailField(
        label='Email',
        max_length=50,
        min_length=3,
        required=True,
        widget=widgets.EmailInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "email@email.com",
        }),
        error_messages={
            'min_length': "Email inválido.",
            'invalid': "Email inválido.",
        }
    )

    initial = {
        'email': '',
    }

@parsleyfy
class LoginForm(AuthenticationForm):
    """
    Classe do formulário de autenticação de Login
    """

    # Classe de Metadados
    class Meta:
        fields = ['username', 'password']

        parsley_extras = {
            'username': {
                'remote': reverse_lazy('parsley-verificar-email'),
                'remote-message': "O Email digitado não está cadastrado no sistema."
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(LoginForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def confirm_login_allowed(self, user):
        """
        Metódo para confirmar a autorização de Login
        """
        # Verifica se o usuário está ativo
        if not user.is_active:
            raise forms.ValidationError(('Sua conta não está ativa.' \
                                         'Verifique as mensagens em seu email.'),
                                        code='inactive',)

    form_name = 'login-form'
    scope_prefix = 'dados_login'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    # Email
    username = forms.EmailField(
        label='Email',
        max_length=50,
        min_length=3,
        required=True,
        widget=widgets.EmailInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "email@email.com",
        }),
        error_messages={
            'min_length': "Email inválido.",
            'invalid': "Email inválido.",
        }
    )

    password = forms.CharField(
        label='Senha',
        max_length=16,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'placeholder': "Senha",
        })
    )

    initial = {
        'username': '',
        'password': '',
    }

@parsleyfy
class VenderCriptomoedaForm(Form):
    """
    Classe do formulário de venda de criptomoeda
    """

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        lista = kwargs.pop('lista')
        super(VenderCriptomoedaForm, self).__init__(*args, **kwargs)
        # Adiciona a lista de criptomoedas atualizada
        self.fields['criptomoeda'].choices = lista
        # Adicionar as classes CSS
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'criptomoeda_form'
    scope_prefix = 'dados_criptomoeda'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    criptomoeda = forms.ChoiceField(
        label='Criptomoeda',
        required=True,
        widget=widgets.Select(attrs={
            'data-parsley-trigger':"focusin focusout",
        }),
        help_text='Escolha a criptomoeda desejada.'
    )

    parar_compras = forms.BooleanField(
        label='Parar compras de criptomoedas',
        required=False,
        widget=widgets.CheckboxInput(),
        initial=False,
        help_text='Parar todas as compras de criptomoedas porém, as ordens ativas permanecem \
                   até serem vendidas.'
    )

    initial = {
        'criptomoeda': '',
        'parar_compras': False,
    }

@parsleyfy
class ComprarCriptomoedaForm(Form):
    """
    Classe do formulário de compra de criptomoeda
    """

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        lista = kwargs.pop('lista')
        super(ComprarCriptomoedaForm, self).__init__(*args, **kwargs)
        # Adiciona a lista de criptomoedas atualizada
        self.fields['criptomoeda'].choices = lista
        # Adicionar as classes CSS
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'criptomoeda_form'
    scope_prefix = 'dados_criptomoeda'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    criptomoeda = forms.ChoiceField(
        label='Criptomoeda',
        required=True,
        widget=widgets.Select(attrs={
            'data-parsley-trigger':"focusin focusout",
        }),
        help_text='Escolha a criptomoeda desejada.'
    )

    initial = {
        'criptomoeda': '',
    }

@parsleyfy
class CarteiraForm(ModelForm):
    """
    Classe do formulário de cadastro do Usuário
    """

    # Classe de Metadados
    class Meta:
        model = CarteiraCriptomoeda
        # Pegar os campos do model
        fields = ['simulacao', 'saldo', 'chave_api', 'chave_secreta', 'num_operacoes']

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(CarteiraForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        # exceto o campo 'usuario'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'carteira_form'
    scope_prefix = 'dados_carteira'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    simulacao = forms.BooleanField(
        label='Modo de simulação',
        required=False,
        widget=widgets.CheckboxInput(),
        initial=True,
        help_text='Com o modo de simulação ativado não será utilizado o saldo da carteira \
                   se for verdadeira.'
    )

    saldo = forms.FloatField(
        label='Saldo a ser utilizado',
        required=True,
        widget=widgets.NumberInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Saldo",
            'min': '0.006',
            'step':'0.001',
            'autocomplete': "off",
        }),
        help_text='Digite o saldo em Bitcoins a ser utilizado da carteira. \
                   Minímo é de 0.006 Bitcoin.'
    )

    chave_api = forms.CharField(
        label='Chave da API',
        max_length=128,
        required=False,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Chave da API",
            'autocomplete': "off",
        }),
        help_text='Digite a chave da API'
    )

    chave_secreta = forms.CharField(
        label='Chave Secreta',
        max_length=128,
        required=False,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Chave Secreta",
            'autocomplete': "off",
        }),
        help_text='Digite a chave secreta da API'
    )

    num_operacoes = forms.IntegerField(
        label='Operações',
        required=True,
        widget=widgets.NumberInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Número de operações",
            'max': '3',
            'min': '1',
            'step':'1',
            'autocomplete': "off",
        }),
        help_text='Digite o número máximo de operações que o Robô irá efetuar simultaneamente, \
                   utilizando o saldo. Máximo 3 operações e minímo 1 operação.'
    )

    initial = {
        'simulacao': True,
        'saldo': '',
        'chave_api': '',
        'chave_secreta': '',
        'num_operacoes': '',
    }


@parsleyfy
class AtualizarUsuarioForm(ModelForm):
    """
    Classe do formulário de atualização de dados cadastrais do Usuário
    """

    # Classe de Metadados
    class Meta:
        model = Usuario
        # Pegar todos campos do model
        fields = ['first_name', 'last_name', 'cpf', 'telefone', 'email']

        parsley_extras = {
            'cpf': {
                'remote': reverse_lazy('parsley-validar-cpf'),
                'remote-message': "O CPF digitado está sendo utilizado por outro usuário \
                                    ou é inválido."
            },
            'email': {
                'remote': reverse_lazy('parsley-validar-email'),
                'remote-message': "O Email digitado está sendo utilizado por outro usuário."
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(AtualizarUsuarioForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        # exceto o campo 'termos_uso'
        for field in self.fields:
            if field != 'termos_uso':
                self.fields[field].widget.attrs['class'] = 'form-control'

    form_name = 'cadastro_form'
    scope_prefix = 'dados_cadastro'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    # Iniciliza o validador de CPF
    validar_cpf = BRCPFValidator()

    first_name = forms.CharField(
        label='Nome',
        max_length=50,
        min_length=2,
        required=True,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Nome",
        }),
        help_text='Digite o seu nome',
        error_messages={
            'min_length': "O tamanho do nome é muito curto.",
        }
    )

    last_name = forms.CharField(
        label='Sobrenome',
        max_length=50,
        min_length=2,
        required=True,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Sobrenome",
        }),
        help_text='Digite o seu sobrenome',
        error_messages={
            'min_length': "O tamanho do sobrenome é muito curto.",
        }
    )

    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        min_length=14,
        required=False,
        disabled=True,
        validators=[validar_cpf],
        widget=widgets.TextInput(attrs={
            'data-mask':"000.000.000-00",
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "000.000.000-00",
        }),
        help_text='CPF cadastrado',
        error_messages={
            'min_length': "O tamanho do CPF é muito curto.",
            'invalid': "O CPF digitado é inválido.",
        }
    )

    telefone = forms.CharField(
        label='Telefone',
        max_length=14,
        min_length=13,
        required=True,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "(00)00000-0000",
        }),
        help_text='Digite o seu número de telefone',
        error_messages={
            'min_length': "O tamanho do telefone é muito curto.",
        }
    )

    email = forms.EmailField(
        label='Email',
        max_length=50,
        min_length=3,
        required=True,
        widget=widgets.EmailInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "email@email.com",
        }),
        help_text='Digite o seu email',
        error_messages={
            'min_length': "O tamanho do email é muito curto.",
            'invalid': "Digite um endereço de email válido.",
        }
    )

@parsleyfy
class UsuarioForm(ModelForm):
    """
    Classe do formulário de cadastro do Usuário
    """

    # Classe de Metadados
    class Meta:
        model = Usuario
        # Pegar todos campos do model
        fields = ['first_name', 'last_name', 'cpf', 'telefone', 'email', 'password']

        parsley_extras = {
            'cpf': {
                'remote': reverse_lazy('parsley-validar-cpf'),
                'remote-message': "O CPF digitado está sendo utilizado por outro usuário \
                                    ou é inválido."
            },
            'email': {
                'remote': reverse_lazy('parsley-validar-email'),
                'remote-message': "O Email digitado está sendo utilizado por outro usuário."
            },
            'password': {
                'remote': reverse_lazy('parsley-validar-senha'),
                'remote-message': "Digite uma senha com números e caracteres"
            },
            'confirmar_senha': {
                'equalto': "password",
                'error-message': "As senhas digitadas não são iguais",
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Metódo de inicialização do Form
        """
        super(UsuarioForm, self).__init__(*args, **kwargs)
        # Adicionar a classe CSS 'form-control' para todos os campos do formulário
        # exceto o campo 'termos_uso'
        for field in self.fields:
            if field != 'termos_uso':
                self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        """
        Metódo para salvar o Form
        """
        usuario = super(UsuarioForm, self).save(commit=False)
        # Criptografar senha do usuário antes de realizar o Commit
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario

    form_name = 'cadastro_form'
    scope_prefix = 'dados_cadastro'

    # Adicionar a classe CSS 'djng-field-required' para campos obrigatórios
    required_css_class = 'field-required'

    # Iniciliza o validador de CPF
    validar_cpf = BRCPFValidator()

    first_name = forms.CharField(
        label='Nome',
        max_length=50,
        min_length=2,
        required=True,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Nome",
        }),
        help_text='Digite o seu nome',
        error_messages={
            'min_length': "O tamanho do nome é muito curto.",
        }
    )

    last_name = forms.CharField(
        label='Sobrenome',
        max_length=50,
        min_length=2,
        required=True,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Sobrenome",
        }),
        help_text='Digite o seu sobrenome',
        error_messages={
            'min_length': "O tamanho do sobrenome é muito curto.",
        }
    )

    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        min_length=14,
        required=True,
        validators=[validar_cpf],
        widget=widgets.TextInput(attrs={
            'data-mask':"000.000.000-00",
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "000.000.000-00",
        }),
        help_text='Digite o seu CPF',
        error_messages={
            'min_length': "O tamanho do CPF é muito curto.",
            'invalid': "O CPF digitado é inválido.",
        }
    )

    telefone = forms.CharField(
        label='Telefone',
        max_length=14,
        min_length=13,
        required=True,
        widget=widgets.TextInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "(00)00000-0000",
        }),
        help_text='Digite o seu número de telefone',
        error_messages={
            'min_length': "O tamanho do telefone é muito curto.",
        }
    )

    email = forms.EmailField(
        label='Email',
        max_length=50,
        min_length=3,
        required=True,
        widget=widgets.EmailInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "email@email.com",
        }),
        help_text='Digite o seu email',
        error_messages={
            'min_length': "O tamanho do email é muito curto.",
            'invalid': "Digite um endereço de email válido.",
        }
    )

    password = forms.CharField(
        label='Senha',
        max_length=16,
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'data-parsley-remote-options':'{ "type": "POST", "dataType": "json" }',
            'placeholder': "Senha",
            'autocomplete': "off",
        }),
        help_text='Digite a sua senha',
        error_messages={
            'min_length': "O tamanho da senha é muito curta.",
        }
    )

    confirmar_senha = forms.CharField(
        label='Reinsira sua senha',
        max_length=16,
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(attrs={
            'data-parsley-trigger':"focusin focusout",
            'placeholder': "Senha",
            'autocomplete': "off",
        }),
        help_text='Digite a sua senha novamente',
        error_messages={
            'min_length': "O tamanho da senha é muito curta.",
        }
    )

    termos_uso = forms.BooleanField(
        label='Aceito os Termos de Uso',
        required=True,
        widget=widgets.CheckboxInput(attrs={
            'data-parsley-trigger':"focusin focusout",
        }),
        error_messages={
            'required': "É obrigatório aceitar os Termos de Uso.",
        }
    )

    initial = {
        'first_name': '',
        'last_name': '',
        'cpf': '',
        'email': '',
        'telefone': '',
        'password': '',
        'confirmar_senha': '',
        'termos_uso': False,
    }
