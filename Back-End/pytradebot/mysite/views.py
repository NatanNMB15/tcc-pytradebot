import os
import subprocess
import ast
import json
import urllib3

from requests import Session
from requests.exceptions import Timeout, TooManyRedirects

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.base import RedirectView
from django.shortcuts import render, reverse, render_to_response
from django.contrib.auth.password_validation import get_default_password_validators
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from localflavor.br.validators import BRCPFValidator

from .form import UsuarioForm, AtualizarUsuarioForm, CarteiraForm, \
                  ComprarCriptomoedaForm, VenderCriptomoedaForm
from .models import Usuario, CarteiraCriptomoeda, Trade

def browserconfig(request):
    """
    Metódo para retornar o arquivo browserconfig.xml com a URL dos arquivos estáticos
    """
    static_url = settings.STATIC_URL
    return render(request, 'site-pytradebot/browserconfig.xml',
                  {'static_url': static_url},
                  content_type="text/xml")

def atualizar_json(usuario, form):
    """
    Metódo para salvar/atualizar as configurações do arquivo JSON do usuário
    :param usuario: Parâmetro do objeto usuário
    :param form: Parâmetro do formulário de dados
    """
    # Salva as configurações de valor por operação, número de operações
    # saldo, chave da API e chave secreta no arquivo de configurações JSON do usuário
    usuario.config_json['max_open_trades'] = form.cleaned_data['num_operacoes']
    # Valor de cada operação é = Saldo / Número de operações
    usuario.config_json['stake_amount'] = float(form.cleaned_data['saldo']
                                                / form.cleaned_data['num_operacoes'])
    usuario.config_json['dry_run'] = form.cleaned_data['simulacao']
    usuario.config_json['dry_run_wallet'] = form.cleaned_data['saldo']
    usuario.config_json['exchange']['key'] = form.cleaned_data['chave_api']
    usuario.config_json['exchange']['secret'] = form.cleaned_data['chave_secreta']
    usuario.save()

def comando_robo(pytradebot_id, comando, **kwargs):
    """
    Execute o subprocesso da API Rest do Software de Trading
    :param pytradebot_id: Parâmetro de id do robô com o id do usuário
    :param *args: Argumentos
    :param **kwargs: Argumentos adicionais
    :param comando: Comando para ser executado
    :return: Retorna o processo
    """
    saida = {
        "out": "out",
        "err": "err",
        "code": "code"
    }
    # Se houver parâmetro adicional
    if 'adicional' in kwargs:
        adicional = kwargs.get('adicional', None)
        process = subprocess.Popen(['python', 'mysite/scripts/rest_client.py',
                                    '--config', 'mysite/scripts/rest_config.json',
                                    '--hostname', f'{pytradebot_id}', f'{comando}',
                                    f'{adicional}'],
                                   stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(['python', 'mysite/scripts/rest_client.py',
                                    '--config', 'mysite/scripts/rest_config.json',
                                    '--hostname', f'{pytradebot_id}', f'{comando}'],
                                   stdout=subprocess.PIPE)
    # Termina o subprocesso e o retorna
    saida['out'], saida['err'] = process.communicate()
    saida['code'] = process.returncode
    return saida

def status_robo(pytradebot_id):
    """
    Metódo para retornar o estado do robô e atualizar o saldo da carteira
    :param pytradebot_id: Parâmetro de id do robô com o id do usuário
    :return: Retorna um dicionário contendo o estado e a ação
    """
    resultado = {
        "estado": "Offline",
        "acao": "iniciar"
    }
    # Chama o método para executar o comando do robô para verificar se está online
    process = comando_robo(pytradebot_id=pytradebot_id, comando='online')
    # Se o robô estiver sendo executado o processo retorna código 0
    if process['code'] == 0:
        # Remove os caracteres desnecessários
        convert_output = str(process['out']).lstrip('(b"[')
        convert_output2 = convert_output.rstrip(f']\\n"')
        # Converte para uma tuple
        json_tuple = ast.literal_eval(convert_output2)
        # Verificar o estado do robô
        if json_tuple['status'] == 'stopped':
            resultado['estado'] = 'Parado'
            resultado['acao'] = 'retomar'
        elif json_tuple['status'] == 'running':
            resultado['estado'] = 'Operando'
            resultado['acao'] = 'parar'
        elif json_tuple['status'] == 'running-no-buy':
            resultado['estado'] = 'Operando (Sem Comprar)'
            resultado['acao'] = 'parar'

    user_model = get_user_model()
    usuario = user_model.objects.get(pk=pytradebot_id)
    # Se o usuário tiver carteira cadastrada
    if CarteiraCriptomoeda.objects.filter(usuario=usuario).exists():
        # Verifica se o robô está operando
        if resultado['estado'] == 'Operando (Sem Comprar)' or resultado['estado'] == 'Operando':
            carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
            # Executa um subprocesso com o comando para retornar o saldo da carteira
            # com base do saldo na Exchange
            process = comando_robo(pytradebot_id=pytradebot_id, comando='balance')
            # Se o processo retornar código 0 (sucesso)
            if process['code'] == 0:
                # Remove os caracteres desnecessários
                convert_output = str(process['out']).lstrip('(b"[')
                convert_output2 = convert_output.rstrip(f']\\n"')
                # Converte para uma tuple
                json_tuple = ast.literal_eval(convert_output2)
                # Converte a tuple para String, trocando aspas simples para aspas duplas
                # e depois converte a String para JSON
                json_string = json.loads(str(json_tuple).replace("\'", "\""))
                # Pega o saldo total equivalente em Bitcoin e
                # converte para float com 2 casas decimais
                temp_btc = float(json_string['total'])
                saldo_btc = format(temp_btc, '.8f')
                carteira.saldo = saldo_btc
                carteira.save()

    return resultado

def parsley_verificar_email(request):
    """
    Metódo para verificar se o Email digitado pelo usuário está cadastrado
    """
    status_code = 200
    # Pega o email com o dado enviado pelo POST como 'username'
    email = request.POST.get('username', False)
    if request.is_ajax():
        if not email:
            # Tenta pegar o email com o dado enviado pelo POST como 'email'
            email = request.POST.get('email', False)
        user_model = get_user_model()
        # Verifica se o email digitado está cadastrado
        if user_model.objects.filter(email=email).exists():
            data = {'status': 'valid'}
        else:
            data = {'status': 'invalid'}
            status_code = 404
        return JsonResponse(data, status=status_code)

def parsley_validar_email(request):
    """
    Metódo para verificar se o Email digitado pelo usuário não está cadastrado
    """
    status_code = 200
    # Pega o email com o dado enviado pelo POST como 'email'
    email = request.POST.get('email', False)
    if request.is_ajax():
        user_model = get_user_model()
        # Verifica se o email digitado não está cadastrado
        if not user_model.objects.filter(email=email).exists():
            data = {'status': 'valid'}
        else:
            usuario = request.user
            # Caso o usuário esteja logado, verifica se o Email existente é dele
            if usuario is not None \
                and user_model.objects.filter(email=usuario.email).exists():
                data = {'status': 'valid'}
            # Senão é inválido porque pertence a outro usuário
            else:
                data = {'status': 'invalid'}
                status_code = 404
        return JsonResponse(data, status=status_code)

def parsley_validar_cpf(request):
    """
    Metódo para verificar se já existe Usuário com o CPF digitado pelo usuário
    """
    status_code = 200
    # Pega o CPF com o dado enviado pelo POST como 'cpf'
    cpf = request.POST.get('cpf', False)
    if request.is_ajax():
        # Iniciliza o validador de CPF
        validar_cpf = BRCPFValidator()
        try:
            # Realiza a validação do CPF
            validar_cpf(cpf)
            user_model = get_user_model()
            # Verifica se o CPF digitado não está cadastrado
            if not user_model.objects.filter(cpf=cpf).exists():
                data = {'status': 'valid'}
            else:
                usuario = request.user
                # Caso o usuário esteja logado, verifica se o CPF existente é dele
                if usuario is not None \
                    and user_model.objects.filter(cpf=usuario.cpf).exists():
                    data = {'status': 'valid'}
                # Senão é inválido porque pertence a outro usuário
                else:
                    data = {'status': 'invalid'}
                    status_code = 404
            return JsonResponse(data, status=status_code)
        # Se houver erro de validação é inválido
        except ValidationError:
            data = {'status': 'invalid'}
            status_code = 404
            return JsonResponse(data, status=status_code)

def parsley_validar_senha(request):
    """
    Metódo para verificar se a senha digitada pelo usuário
    possui os requisitos minímos de segurança, de acordo com o validador de senhas do Django
    """
    status_code = 200
    # Pega a senha com o dado enviado pelo POST como 'password'
    senha = request.POST.get('password', False)
    if request.is_ajax():
        if not senha:
            # Tenta pegar a senha com o dado enviado pelo POST como 'new_password1'
            senha = request.POST.get('new_password1', False)
            # Se não houver senha é inválido
            if not senha:
                status_code = 404
                data = {'status': 'invalid'}
                return JsonResponse(data, status=status_code)
        # Realiza a validação de senha com os requisitos minímos de segurança
        validar_senha = get_default_password_validators()
        for validator in validar_senha:
            try:
                # Realiza a validação da senha
                validator.validate(senha)
            # Se houver erro de validação é inválido
            except ValidationError:
                status_code = 404
                data = {'status': 'invalid'}
                return JsonResponse(data, status=status_code)
        data = {'status': 'valid'}
        return JsonResponse(data, status=status_code)

def ativar_cadastro(request, uidb64, token):
    """
    Metódo para ativar o cadastro do usuário pela confirmação de email
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user_model = get_user_model()
        usuario = user_model.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        usuario = None
    # Verifica se o usuário não está ativo, se existe e
    # se o Token passado pela URL é valido para o usuário
    if not usuario.is_active and usuario is not None \
        and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        # Enviar email de confirmação para o usuário
        assunto = 'Cadastro realizado com sucesso'
        html_template = get_template('site-pytradebot/email/cadastro_sucesso.htm')
        html = html_template.render({'nome':str(usuario.first_name),
                                     'sobrenome':str(usuario.last_name),
                                     'email':str(usuario.email)})
        enviar_email = EmailMultiAlternatives(assunto, to=[str(usuario.email)])
        enviar_email.attach_alternative(html, "text/html")
        enviar_email.send(fail_silently=False)
        return render(request, 'site-pytradebot/conta/ativacao_sucesso.html')
    return HttpResponse('Link de ativação inválido!')

@method_decorator(cache_page(60 * 15), name='dispatch')
class Cadastro(CreateView): # pylint: disable=too-many-ancestors
    """
    Class de cadastro do formulário
    """
    model = Usuario
    template_name = 'site-pytradebot/cadastro.html'
    form_class = UsuarioForm

    def form_valid(self, form):
        """
        Metódo chamado caso o formulário de cadastro seja válido, utilizando metódo POST
        """
        try:
            usuario = form.save(commit=False)
            # Desativa o usuário enquanto o email não for confirmado
            usuario.is_active = False
            usuario.save()
            # Gera um ID e token de confirmação para o email
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            # Enviar email de confirmação para o usuário
            assunto = 'Confirmar Email'
            html_template = get_template('site-pytradebot/email/confirmar_email.htm')
            html = html_template.render({'nome':str(usuario.first_name),
                                         'sobrenome':str(usuario.last_name),
                                         'uid':uid,
                                         'token':token,
                                         'email':str(usuario.email)})
            enviar_email = EmailMultiAlternatives(assunto, to=[str(usuario.email)])
            enviar_email.attach_alternative(html, "text/html")
            enviar_email.send(fail_silently=False)
            # Define a URL de sucesso, ou seja, acessa a URL
            # se o formulário foi enviado com sucesso. Também passando a variável de
            # email para o template como argumento
            return render(self.request, 'site-pytradebot/conta/confirmar_email.html',
                          {'email':str(usuario.email)})
        except BadHeaderError:
            return HttpResponse('Header de email inválido.')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class AlterarCadastro(UpdateView): # pylint: disable=too-many-ancestors
    """
    Class de cadastro do formulário
    """
    model = Usuario
    template_name = 'site-pytradebot/dadosusuario.html'
    form_class = AtualizarUsuarioForm
    success_url = reverse_lazy('painelcontrole')

    def get_context_data(self, **kwargs):
        """
        Metódo para pegar informações do usuário logado através do objeto usuário,
        renderizando o template com os dados do usuário
        """
        context = super(AlterarCadastro, self).get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context

@login_required
def carteiralistar(request):
    """
    Metódo para retornar o template de listar carteiras
    """
    usuario = request.user
    try:
        # Pega o objeto carteira se já existir
        carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
        # Pega a chave da API e o saldo
        chave_api = carteira.chave_api
        saldo = carteira.saldo
        valor_operacao = carteira.valor_operacao
        num_operacoes = carteira.num_operacoes
        simulacao = carteira.simulacao
        existe_carteira = True
    # Se não tiver carteira cadastrada deixe em branco
    except ObjectDoesNotExist:
        chave_api = ""
        saldo = ""
        valor_operacao = ""
        num_operacoes = ""
        simulacao = ""
        existe_carteira = False
    return render(request, 'site-pytradebot/carteiralistar.html',
                  {'usuario':usuario, 'chave_api':chave_api, 'saldo':saldo,
                   'valor_operacao':valor_operacao, 'num_operacoes':num_operacoes,
                   'simulacao':simulacao, 'existe_carteira':existe_carteira})

@method_decorator(login_required, name='dispatch')
class CarteiraAtualizar(UpdateView): # pylint: disable=too-many-ancestors
    """
    Classe para atualizar carteira
    """
    model = CarteiraCriptomoeda
    template_name = 'site-pytradebot/carteiraadicionar.html'
    form_class = CarteiraForm
    success_url = reverse_lazy('carteiralistar')

    def get_initial(self):
        """
        Metódo para retornar os valores inicias do formulário
        redefinindo os valores "chave_api", "chave_secreta" e "saldo"
        """
        initial = super(CarteiraAtualizar, self).get_initial()
        initial['chave_api'] = ''
        initial['chave_secreta'] = ''
        initial['saldo'] = ''
        return initial

    def form_valid(self, form):
        """
        Metódo para salvar o formulário válido com o objeto usuário do usuário autenticado
        """
        # Pega o modelo atual de usuário e pega o objeto usuário do banco de dados
        # com base na chave primária do usuário autenticado
        user_model = get_user_model()
        usuario = user_model.objects.get(pk=self.request.user.pk)
        id_usuario = usuario.pk
        # Chama o metódo para atualizar os dados JSON do usuário
        atualizar_json(usuario=usuario, form=form)
        # Chama o método para executar o comando de recarregar as configurações do robô
        comando_robo(pytradebot_id=id_usuario, comando='reload_conf')
        # Atualiza a carteira de criptomoeda criada com os dados do formulário
        form.instance.usuario = usuario
        form.instance.valor_operacao = float(form.cleaned_data['saldo']
                                             / form.cleaned_data['num_operacoes'])
        return super(CarteiraAtualizar, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Metódo para pegar informações do usuário logado através do objeto usuário,
        renderizando o template com os dados do usuário
        """
        context = super(CarteiraAtualizar, self).get_context_data(**kwargs)
        context['usuario'] = self.request.user
        context['acao'] = "Atualizar"
        return context

@method_decorator(login_required, name='dispatch')
class CarteiraCriar(CreateView): # pylint: disable=too-many-ancestors
    """
    Classe para adicionar carteira
    """
    model = CarteiraCriptomoeda
    template_name = 'site-pytradebot/carteiraadicionar.html'
    form_class = CarteiraForm
    success_url = reverse_lazy('carteiralistar')

    def form_valid(self, form):
        """
        Metódo para salvar o formulário válido com o objeto usuário do usuário autenticado
        """
        # Pega o modelo atual de usuário e pega o objeto usuário do banco de dados
        # com base na chave primária do usuário autenticado
        user_model = get_user_model()
        usuario = user_model.objects.get(pk=self.request.user.pk)
        # Chama o metódo para atualizar os dados JSON do usuário
        atualizar_json(usuario=usuario, form=form)
        # Salva a carteira de criptomoeda criada com os dados do formulário
        form.instance.usuario = usuario
        form.instance.valor_operacao = float(form.cleaned_data['saldo']
                                             / form.cleaned_data['num_operacoes'])
        return super(CarteiraCriar, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Metódo para pegar informações do usuário logado através do objeto usuário,
        renderizando o template com os dados do usuário
        """
        context = super(CarteiraCriar, self).get_context_data(**kwargs)
        context['usuario'] = self.request.user
        context['acao'] = "Adicionar"
        return context

@method_decorator(login_required, name='dispatch')
class CarteiraAdicionar(RedirectView): # pylint: disable=too-many-ancestors
    """
    Classe para redirecionar o usuário para criar carteira caso não tenha cadastrado
    ou atualizar carteira caso possua.
    """
    permanent = False
    query_string = False
    pattern_name = 'carteiraadicionar'

    def get_redirect_url(self, *args, **kwargs):
        """
        Metódo para redirecionar para URL de criar ou atualizar a carteira
        """
        try:
            # Pega o modelo atual de usuário e pega o objeto usuário do banco de dados
            # com base na chave primária do usuário autenticado
            user_model = get_user_model()
            usuario = user_model.objects.get(pk=self.request.user.pk)
            # Se existir carteira redirecione para a view de atualizar a carteira
            carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
            return reverse('carteiraatualizar',
                           kwargs={'pk': carteira.pk})
        # Se não existir redirecione para a view de criar carteira
        except ObjectDoesNotExist:
            return reverse('carteiracriar')

@method_decorator(login_required, name='dispatch')
class VenderCriptomoeda(FormView): # pylint: disable=too-many-ancestors
    """
    Classe para vender criptomoedas
    """
    template_name = 'site-pytradebot/transacaovender.html'
    form_class = VenderCriptomoedaForm
    success_url = reverse_lazy('transacaohistorico')

    def form_valid(self, form):
        """
        Metódo para verificar se o formulário é válido, se for efetua a compra da criptomoeda
        """
        try:
            usuario = self.request.user
            id_usuario = usuario.pk
            criptomoeda = str(form.cleaned_data['criptomoeda'])
            vender = criptomoeda
            # Verifica se o usuário quer vender uma moeda específica
            if criptomoeda != 'all':
                trade = Trade.objects.get(user=usuario, pair=criptomoeda, is_open=True)
                vender = trade.id
            # Executa um subprocesso com o comando para forçar vender a(s) criptomoeda(s)
            process = comando_robo(pytradebot_id=id_usuario, comando='forcesell', adicional=vender)
            # Se o processo não retornar código 0, exibe o erro
            if process['code'] != 0:
                return render(self.request,
                              'site-pytradebot/erros/vender-criptomoeda-erro.html',
                              {'usuario':usuario})

            parar_compras = bool(form.cleaned_data['parar_compras'])
            if parar_compras is True:
                # Executa um subprocesso com o comando para forçar vender a(s) criptomoeda(s)
                process_1 = comando_robo(pytradebot_id=id_usuario, comando='stopbuy')
                # Se o processo não retornar código 0, exibe o erro
                if process_1['code'] != 0:
                    return render(self.request,
                                  'site-pytradebot/erros/vender-criptomoeda-erro.html',
                                  {'usuario':usuario})
        # Se o trade da criptomoeda não existir
        except ObjectDoesNotExist:
            return render(self.request,
                          'site-pytradebot/erros/vender-criptomoeda-vendida.html',
                          {'usuario':usuario})
        return super(VenderCriptomoeda, self).form_valid(form)

    def get_form_kwargs(self):
        """
        Método para passar a lista de criptomoedas atualizada como argumento para
        construir o formulário
        """
        kwargs = super(VenderCriptomoeda, self).get_form_kwargs()
        usuario = self.request.user
        lista = []
        tudo = ("all", "Tudo")
        lista.append(tudo)
        # Pega todos os trades ativos do usuário
        for trade in Trade.objects.filter(user=usuario, is_open=True):
            temp = (trade.pair, trade.pair)
            lista.append(temp)
        kwargs['lista'] = lista
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Metódo para pegar informações do usuário logado através do objeto usuário,
        renderizando o template com os dados do usuário
        """
        context = super(VenderCriptomoeda, self).get_context_data(**kwargs)
        usuario = self.request.user
        id_usuario = usuario.pk
        context['usuario'] = usuario
        try:
            carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
            context['valor'] = carteira.valor_operacao
        # Se não existir carteira de criptomoedas cadastrada
        except ObjectDoesNotExist:
            context['valor'] = ''
        trades = Trade.objects.filter(user=usuario, is_open=True).count()
        context['trades'] = trades
        resultado = status_robo(pytradebot_id=id_usuario)
        context['estado'] = resultado['estado']
        return context

@method_decorator(login_required, name='dispatch')
class ComprarCriptomoeda(FormView): # pylint: disable=too-many-ancestors
    """
    Classe para comprar criptomoeda
    """
    template_name = 'site-pytradebot/transacaocomprar.html'
    form_class = ComprarCriptomoedaForm
    success_url = reverse_lazy('transacaohistorico')

    def form_valid(self, form):
        """
        Metódo para verificar se o formulário é válido, se for efetua a compra da criptomoeda
        """
        usuario = self.request.user
        id_usuario = usuario.pk
        criptomoeda = str(form.cleaned_data['criptomoeda'])
        # Executa um subprocesso com o comando para forçar comprar a criptomoeda
        process = comando_robo(pytradebot_id=id_usuario, comando='forcebuy', adicional=criptomoeda)
        # Se o processo não retornar código 0, exibe o erro
        if process['code'] != 0:
            return render(self.request, 'site-pytradebot/erros/comprar-criptomoeda-erro.html',
                          {'usuario':usuario})
        return super(ComprarCriptomoeda, self).form_valid(form)

    def get_form_kwargs(self):
        """
        Método para passar a lista de criptomoedas atualizada como argumento para
        construir o formulário
        """
        kwargs = super(ComprarCriptomoeda, self).get_form_kwargs()
        usuario = self.request.user
        id_usuario = usuario.pk
        # Executa um subprocesso com o comando para retornar a lista de criptomoedas
        process = comando_robo(pytradebot_id=id_usuario, comando='whitelist')
        # Se o processo retornar código 0 (sucesso)
        if process['code'] == 0:
            # Remove os caracteres desnecessários
            convert_output = str(process['out']).lstrip('(b"[')
            convert_output2 = convert_output.rstrip(f']\\n"')
            # Converte para uma tuple
            json_tuple = ast.literal_eval(convert_output2)
            temp_lista = json_tuple['whitelist']
            lista = []
            # Enumera os items da lista de criptomoedas
            for i, (j) in enumerate(temp_lista):
                # Verifica se a criptomoeda não possui ordem ativa
                if not Trade.objects.filter(user=usuario, is_open=True, pair=j).count():
                    temp = (j, j)
                    lista.append(temp)
        # Se não coloca uma lista vazia
        else:
            lista = [('1', '---')]
        kwargs['lista'] = lista
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Metódo para pegar informações do usuário logado através do objeto usuário,
        renderizando o template com os dados do usuário
        """
        context = super(ComprarCriptomoeda, self).get_context_data(**kwargs)
        usuario = self.request.user
        id_usuario = usuario.pk
        context['usuario'] = usuario
        try:
            carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
            context['valor'] = carteira.valor_operacao
            context['operacoes'] = carteira.num_operacoes
        # Se não existir carteira de criptomoedas cadastrada
        except ObjectDoesNotExist:
            context['valor'] = ''
            context['operacoes'] = ''
        trades = Trade.objects.filter(user=usuario, is_open=True).count()
        context['trades'] = trades
        resultado = status_robo(pytradebot_id=id_usuario)
        context['estado'] = resultado['estado']
        return context

@login_required
def estrategiaadicionar(request):
    """
    Metódo para retornar o template de estratégia adicionar
    """
    usuario = request.user
    return render(request, 'site-pytradebot/estrategiaadicionar.html', {'usuario':usuario})

@login_required
def estrategiacriar(request):
    """
    Metódo para retornar o template para criar estratégia
    """
    usuario = request.user
    return render(request, 'site-pytradebot/estrategiacriar.html', {'usuario':usuario})

@login_required
def estrategialistar(request):
    """
    Metódo para retornar o template de estratégia listar
    """
    usuario = request.user
    return render(request, 'site-pytradebot/estrategialistar.html', {'usuario':usuario})

@login_required
def estrategiateste(request):
    """
    Metódo para retornar o template para testar estratégia
    """
    usuario = request.user
    return render(request, 'site-pytradebot/estrategiateste.html', {'usuario':usuario})

@login_required
@cache_page(60 * 15)
def graficos(request):
    """
    Metódo para retornar o template de gráficos
    """
    usuario = request.user
    return render(request, 'site-pytradebot/graficos.html', {'usuario':usuario})

@cache_page(60 * 15)
def index(request):
    """
    Metódo para retornar o template índice do site
    """
    return render(request, 'site-pytradebot/index.html')

@cache_page(60 * 15)
def index_graficos(request):
    """
    Metódo para retornar o template gráficos sem estar logado
    """
    return render(request, 'site-pytradebot/index_graficos.html')

def converter_real_bitcoin(quantidade):
    """
    Metódo para converter Bitcoin para Real utilizando a BlockChain Info
    utilizando dados em tempo real
    """

    url = 'https://blockchain.info/ticker'
    headers = {
        'Accepts': 'application/json',
    }

    session = Session()
    session.headers.update(headers)

    try:
        # Tenta realizar a requisição da API
        response = session.get(url)
        # Pega o resultado dos dados em JSOn
        data = json.loads(response.text)
        temp_resultado = data['BRL']['last'] * quantidade
        resultado = format(temp_resultado, '.2f')
        return resultado
    except (ConnectionError, Timeout, TooManyRedirects):
        return 0

@login_required
@cache_page(60 * 15)
def painelcontrole(request):
    """
    Metódo para retornar o template de painel de controle
    """
    usuario = request.user
    id_usuario = usuario.pk
    resultado = status_robo(pytradebot_id=id_usuario)
    carteira = None
    # Se o usuário tiver carteira cadastrada
    if CarteiraCriptomoeda.objects.filter(usuario=usuario).exists():
        # Verifica se o robô está operando
        if resultado['estado'] == 'Operando (Sem Comprar)' or resultado['estado'] == 'Operando':
            carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
            trades = Trade.objects.filter(user=usuario, is_open=False)
            porc_lucro = 0
            # Percorre todos os trades fechados e calcula o saldo
            for i in trades:
                porc_lucro += i.close_profit
            # Pega o saldo Bitcoin da carteira
            saldo_btc = carteira.saldo
            # Se estiver no modo de simulação
            if carteira.simulacao:
                # Realiza o cálculo da porcentagem do lucro com o saldo fictício
                saldo_btc = saldo_btc * (porc_lucro + 1)
            # Chama o método para converter Bitcoin para real
            temp_real = converter_real_bitcoin(quantidade=saldo_btc)
            saldo_real = 'R$ ' + str(temp_real)
            # Normaliza a porcentagem de lucro
            porc_lucro = porc_lucro * 100
            temp_lucro = format(porc_lucro, '.2f')
            lucro = str(temp_lucro) + '%'
        else:
            saldo_btc = 'Robô não está operando'
            saldo_real = 'Robô não está operando'
            lucro = 'Robô não está operando'
    else:
        saldo_btc = 'Carteira não cadastrada'
        saldo_real = 'Carteira não cadastrada'
        lucro = 'Carteira não cadastrada'
    acao_reiniciar = 'reiniciar'
    acao_parar_compras = 'parar-compras'
    acao_remover = 'remover'
    return render(request, 'site-pytradebot/painelcontrole.html',
                  {'usuario':usuario,
                   'estado':resultado['estado'],
                   'acao':resultado['acao'],
                   'acao_reiniciar':acao_reiniciar,
                   'acao_parar_compras':acao_parar_compras,
                   'acao_remover': acao_remover,
                   'saldo_btc': saldo_btc,
                   'saldo_real': saldo_real,
                   'lucro': lucro})

@login_required
def ajax_painel_controle(request):
    """
    Metódo para retornar os componentes do painel de controle
    """
    usuario = request.user
    id_usuario = usuario.pk
    resultado = status_robo(pytradebot_id=id_usuario)
    carteira = None
    # Se o usuário tiver carteira cadastrada
    if CarteiraCriptomoeda.objects.filter(usuario=usuario).exists():
        # Verifica se o robô está operando
        if resultado['estado'] == 'Operando (Sem Comprar)' or resultado['estado'] == 'Operando':
            carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
            trades = Trade.objects.filter(user=usuario, is_open=False)
            porc_lucro = 0
            # Percorre todos os trades fechados e calcula o saldo
            for i in trades:
                porc_lucro += i.close_profit
            # Pega o saldo Bitcoin da carteira
            saldo_btc = carteira.saldo
            # Se estiver no modo de simulação
            if carteira.simulacao:
                # Realiza o cálculo da porcentagem do lucro com o saldo fictício
                saldo_btc = saldo_btc * (porc_lucro + 1)
            # Chama o método para converter Bitcoin para real
            temp_real = converter_real_bitcoin(quantidade=saldo_btc)
            saldo_real = 'R$ ' + str(temp_real)
            # Normaliza a porcentagem de lucro
            porc_lucro = porc_lucro * 100
            temp_lucro = format(porc_lucro, '.2f')
            lucro = str(temp_lucro) + '%'
        else:
            saldo_btc = 'Robô não está operando'
            saldo_real = 'Robô não está operando'
            lucro = 'Robô não está operando'
    else:
        saldo_btc = 'Carteira não cadastrada'
        saldo_real = 'Carteira não cadastrada'
        lucro = 'Carteira não cadastrada'
    acao_reiniciar = 'reiniciar'
    acao_parar_compras = 'parar-compras'
    acao_remover = 'remover'
    return render_to_response('site-pytradebot/ajax_update/painelcontrole.html',
                              {'usuario':usuario,
                               'estado':resultado['estado'],
                               'acao':resultado['acao'],
                               'acao_reiniciar':acao_reiniciar,
                               'acao_parar_compras':acao_parar_compras,
                               'acao_remover': acao_remover,
                               'saldo_btc': saldo_btc,
                               'saldo_real': saldo_real,
                               'lucro': lucro})

def endpoint_containers(pytradebot_id, comando, metodo):
    """
    Metódo para fazer requisições do Web Service para gerenciar containers dos robôs
    """
    http = urllib3.PoolManager()
    url_base = str(os.getenv('BOT_MANAGEMENT_URL'))
    url = f'{url_base}/{comando}?id={pytradebot_id}'
    http_request = http.request(f'{metodo}', url)
    return http_request.status

@login_required
def controlerobo(request, pk, acao):
    """
    Metódo para iniciar, parar, reiniciar ou parar as compras automáticas do robô
    """
    usuario = request.GET.get('username', False)
    id_usuario = pk
    data = {'status': 'valid'}
    status_code = 200
    # Se a ação for iniciar o robô
    if acao == 'iniciar':
        # Chama o método para se comunicar com o Web Service, executando o comando create
        # com o metódo GET
        resultado = endpoint_containers(pytradebot_id=id_usuario,
                                        comando='create', metodo='GET')
        # Se houver erro ao criar o robô
        if resultado != 200:
            return render(request,
                          'site-pytradebot/erros/criar-robo-erro.html',
                          {'usuario':usuario})
    # Se não se a ação for reiniciar robô
    elif acao == 'reiniciar':
        # Chama o método para se comunicar com o Web Service, executando o comando reset
        # com o metódo GET
        resultado = endpoint_containers(pytradebot_id=id_usuario,
                                        comando='reset', metodo='GET')
        # Se houver erro ao criar o robô
        if resultado != 200:
            return render(request,
                          'site-pytradebot/erros/comando-robo-erro.html',
                          {'usuario':usuario})
    # Se não se a ação for reiniciar robô
    elif acao == 'remover':
        # Chama o método para se comunicar com o Web Service, executando o comando remove
        # com o metódo GET
        resultado = endpoint_containers(pytradebot_id=id_usuario,
                                        comando='remove', metodo='GET')
        # Se houver erro ao criar o robô
        if resultado != 200:
            return render(request,
                          'site-pytradebot/erros/comando-robo-erro.html',
                          {'usuario':usuario})
    # Se não se a ação for retomar as operações do robô
    elif acao == 'retomar':
        # Chama o método para executar o comando de reinicar as operações do robô
        process = comando_robo(pytradebot_id=id_usuario, comando='start')
        # Se o processo não retornar código 0, exibe o erro
        if process['code'] != 0:
            return render(request,
                          'site-pytradebot/erros/comando-robo-erro.html',
                          {'usuario':usuario})
    # Se não se a ação for parar as operações do robô
    elif acao == 'parar':
        # Chama o método para executar o comando de parar as operações do robô
        process = comando_robo(pytradebot_id=id_usuario, comando='stop')
        # Se o processo não retornar código 0, exibe o erro
        if process['code'] != 0:
            return render(request,
                          'site-pytradebot/erros/comando-robo-erro.html',
                          {'usuario':usuario})
    # Se não se a ação for parar as compras automáticas do robô
    elif acao == 'parar-compras':
        # Chama o método para executar o comando para parar as compras automáticas do robô
        process = comando_robo(pytradebot_id=id_usuario, comando='stopbuy')
        # Se o processo não retornar código 0, exibe o erro
        if process['code'] != 0:
            return render(request,
                          'site-pytradebot/erros/comando-robo-erro.html',
                          {'usuario':usuario})

    return JsonResponse(data, status=status_code)

@cache_page(60 * 15)
def termosuso_iframe(request):
    """
    Metódo para retornar o template iframe de termos de uso
    """
    return render(request, 'site-pytradebot/termosuso_iframe.html')

@cache_page(60 * 15)
def termosuso(request):
    """
    Metódo para retornar o template de termos de uso
    """
    return render(request, 'site-pytradebot/termosuso.html')

@login_required
def transacaohistorico(request):
    """
    Metódo para retornar o template de histórico de transações
    """
    usuario = request.user
    id_usuario = usuario.pk
    status_robo(pytradebot_id=id_usuario)
    porc_lucro = 0
    # Pega todos os trades referentes ao usuário logado
    trades = Trade.objects.filter(user=usuario).order_by('-is_open', '-close_date')
    # Se o usuário tiver carteira cadastrada
    if CarteiraCriptomoeda.objects.filter(usuario=usuario).exists():
        carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
        trades_fechado = Trade.objects.filter(user=usuario, is_open=False)
        porc_lucro = 0
        # Percorre todos os trades fechados e calcula o saldo
        for i in trades_fechado:
            porc_lucro += i.close_profit
        # Normaliza a porcentagem de lucro
        porc_lucro = porc_lucro * 100
        temp_lucro = format(porc_lucro, '.2f')

    lucro = str(temp_lucro) + '%'

    return render(request, 'site-pytradebot/transacaohistorico.html',
                  {'usuario':usuario, 'trades':trades, 'lucro': lucro})

@login_required
def ajax_historico_transacoes(request):
    """
    Metódo para retornar os componentes do histórico de transações
    """
    usuario = request.user
    id_usuario = usuario.pk
    status_robo(pytradebot_id=id_usuario)
    porc_lucro = 0
    # Pega todos os trades referentes ao usuário logado
    trades = Trade.objects.filter(user=usuario).order_by('-is_open', '-close_date')
    # Se o usuário tiver carteira cadastrada
    if CarteiraCriptomoeda.objects.filter(usuario=usuario).exists():
        carteira = CarteiraCriptomoeda.objects.get(usuario=usuario)
        trades_fechado = Trade.objects.filter(user=usuario, is_open=False)
        porc_lucro = 0
        # Percorre todos os trades fechados e calcula o saldo
        for i in trades_fechado:
            porc_lucro += i.close_profit
        # Normaliza a porcentagem de lucro
        porc_lucro = porc_lucro * 100
        temp_lucro = format(porc_lucro, '.2f')

    lucro = str(temp_lucro) + '%'

    return render(request, 'site-pytradebot/ajax_update/transacaohistorico.html',
                  {'trades':trades, 'lucro': lucro})

@login_required
def transacaovender(request):
    """
    Metódo para retornar o template de vender criptomoedas
    """
    usuario = request.user
    return render(request, 'site-pytradebot/transacaovender.html', {'usuario':usuario})

@cache_page(60 * 15)
def quemsomos(request):
    """
    Metódo para retornar o template de quem somos
    """
    return render(request, 'site-pytradebot/quemsomos.html')

@cache_page(60 * 15)
def valores(request):
    """
    Metódo para retornar o template de valores da empresa
    """
    return render(request, 'site-pytradebot/valores.html')
