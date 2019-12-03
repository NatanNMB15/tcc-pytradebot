from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

from . import views
from .form import LoginForm, CheckResetForm, ResetForm, ChangePasswordForm

SITEMAPS = {
    'static':StaticViewSitemap,
}

urlpatterns = [
    path('', views.index, name='index'),
    path('sitemap.xml', sitemap, {'sitemaps':SITEMAPS}),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
    path('browserconfig.xml', views.browserconfig),
    path('apple-touch-icon.png',
         RedirectView.as_view(url=settings.STATIC_URL + 'apple-touch-icon.png')),
    path('parsley/validarCpf/', views.parsley_validar_cpf, name='parsley-validar-cpf'),
    path('parsley/validarEmail/', views.parsley_validar_email, name='parsley-validar-email'),
    path('parsley/verificarEmail/', views.parsley_verificar_email, name='parsley-verificar-email'),
    path('parsley/validarSenha/', views.parsley_validar_senha, name='parsley-validar-senha'),
    path('cadastro/', views.Cadastro.as_view(), name='cadastro'),
    path('ativar/<str:uidb64>/<str:token>/', views.ativar_cadastro, name='ativar_cadastro'),
    path('senha/redefinir/',
         auth_views.PasswordResetView.as_view(
             template_name='site-pytradebot/conta/senha_redefinir_form.html',
             subject_template_name='site-pytradebot/email/senha_redefinir_assunto.txt',
             html_email_template_name='site-pytradebot/email/senha_redefinir.htm',
             form_class=CheckResetForm),
         name='password_reset'),
    path('senha/redefinir_email/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='site-pytradebot/conta/senha_redefinir_email.html'),
         name='password_reset_done'),
    path('senha/redefinir_confirmar/<str:uidb64>/<str:token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='site-pytradebot/conta/senha_redefinir_form.html',
             form_class=ResetForm),
         name='password_reset_confirm'),
    path('senha/redefinir_completo/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='site-pytradebot/conta/senha_redefinir_completo.html'),
         name='password_reset_complete'),
    path('sistema/carteira/listar/', views.carteiralistar, name='carteiralistar'),
    path('sistema/carteira/adicionar/', views.CarteiraAdicionar.as_view(),
         name='carteiraadicionar'),
    path('sistema/carteira/criar/', views.CarteiraCriar.as_view(),
         name='carteiracriar'),
    path('sistema/carteira/atualizar/<slug:pk>/', views.CarteiraAtualizar.as_view(),
         name='carteiraatualizar'),
    path('sistema/painelcontrole/', views.painelcontrole, name='painelcontrole'),
    path('sistema/ajax_update/painelcontrole/', views.ajax_painel_controle,
         name='ajax_painel_controle'),
    path('sistema/robo/<int:pk>/<str:acao>/', views.controlerobo, name='controlerobo'),
    path('sistema/alterarsenha/',
         auth_views.PasswordChangeView.as_view(
             template_name='site-pytradebot/conta/senha_redefinir_form_logado.html',
             form_class=ChangePasswordForm),
         name='password_change'),
    path('sistema/alterarsenha/pronto/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='site-pytradebot/conta/senha_redefinir_completo.html'),
         name='password_change_done'),
    path('sistema/dadosusuario/<slug:pk>/', views.AlterarCadastro.as_view(), name='dadosusuario'),
    path('sistema/estrategiaadicionar/', views.EstrategiaCriar.as_view(), name='estrategiaadicionar'),
    path('sistema/estrategialistar/', views.estrategialistar, name='estrategialistar'),
    path('sistema/graficos/', views.graficos, name='graficos'),
    path('graficos/', views.index_graficos, name='index_graficos'),
    path('login/',
         auth_views.LoginView.as_view(
             template_name='site-pytradebot/login.html', authentication_form=LoginForm),
         name='login'),
    path('termosuso/', views.termosuso, name='termosuso'),
    path('iframe/termosuso/', views.termosuso_iframe, name='termosuso_iframe'),
    path('sistema/transacaocomprar/', views.ComprarCriptomoeda.as_view(), name='transacaocomprar'),
    path('sistema/transacaohistorico/', views.transacaohistorico, name='transacaohistorico'),
    path('sistema/ajax_update/transacaohistorico/', views.ajax_historico_transacoes,
         name='ajax_historico_transacoes'),
    path('sistema/ajax_update/transacaohistorico/<int:pagina>/', views.ajax_historico_transacoes,
         name='ajax_historico_transacoes'),
    path('sistema/transacaovender/', views.VenderCriptomoeda.as_view(), name='transacaovender'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('quemsomos/', views.quemsomos, name='quemsomos'),
    path('valores/', views.valores, name='valores')
]

# Acessar os arquivos estáticos (CSS, Javascript) se estiver com o Debug ativado
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
