import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from localflavor.br.models import BRCPFField
from .managers import CustomUserManager

class Trade(models.Model):
    """
    Classe modelo para representar os Trades realizados pelo Software de Trading
    """
    exchange = models.CharField(null=True, max_length=32, verbose_name="Exchange")
    pair = models.CharField(null=True, max_length=32, verbose_name="Criptomoedas")
    is_open = models.BooleanField(null=True,
                                  verbose_name="Ordem ativa")
    fee_open = models.FloatField(null=True,
                                 verbose_name="Taxa de compra")
    fee_close = models.FloatField(null=True,
                                  verbose_name="Taxa de venda")
    open_rate = models.FloatField(null=True,
                                  verbose_name="Valor de compra")
    open_rate_requested = models.FloatField(null=True,
                                            verbose_name="Valor de compra requisitado")
    close_rate = models.FloatField(null=True,
                                   verbose_name="Valor de venda")
    close_rate_requested = models.FloatField(null=True,
                                             verbose_name="Valor de venda requisitado")
    close_profit = models.FloatField(null=True, verbose_name="Lucro realizado")
    stake_amount = models.FloatField(null=True, verbose_name="Quantia máxima de compra")
    amount = models.FloatField(null=True, verbose_name="Quantidade")
    open_date = models.DateTimeField(null=True,
                                     verbose_name="Abertura")
    close_date = models.DateTimeField(null=True,
                                      verbose_name="Fechamento")
    open_order_id = models.CharField(null=True, max_length=128, verbose_name="ID da ordem")
    # absolute value of the stop loss
    stop_loss = models.FloatField(null=True, verbose_name="Valor stop-loss")
    # percentage value of the stop loss
    stop_loss_pct = models.FloatField(null=True, verbose_name="Porcentagem stop-loss")
    # absolute value of the initial stop loss
    initial_stop_loss = models.FloatField(null=True, verbose_name="Valor inicial stop-loss")
    # percentage value of the initial stop loss
    initial_stop_loss_pct = models.FloatField(null=True, verbose_name="Porcentagem \
                                                                       inicial stop-loss")
    # stoploss order id which is on exchange
    stoploss_order_id = models.CharField(null=True, max_length=128, verbose_name="ID stop-loss")
    # last update time of the stoploss order on exchange
    stoploss_last_update = models.DateTimeField(null=True,
                                                verbose_name="Última atualização de stop-loss")
    # absolute value of the highest reached price
    max_rate = models.FloatField(null=True, verbose_name="Preço máximo")
    # Lowest price reached
    min_rate = models.FloatField(null=True, verbose_name="Preço minímo")
    sell_reason = models.CharField(null=True, max_length=128, verbose_name="Motivo de venda")
    strategy = models.CharField(null=True, max_length=128, verbose_name="Estratégia")
    ticker_interval = models.IntegerField(null=True, verbose_name="Intervalo de Tempo")
    # user_id PyTradeBot
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )
    status_buy_sell = models.CharField(null=True, max_length=128, verbose_name="Status")

    class Meta:
        db_table = 'trades'

    def __str__(self):
        return str(self.id)

class Estrategia(models.Model):
    """
    Classe modelo de Estratégia
    """
    nome = models.CharField(null=False, max_length=128, verbose_name="Nome da Estratégia")
    template = models.CharField(null=True, max_length=128, verbose_name="Template da Estratégia")
    metricas = JSONField(null=True, verbose_name="Métricas JSON")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )

    class Meta:
        db_table = 'estrategias'

    def __str__(self):
        return self.usuario.email

class CarteiraCriptomoeda(models.Model):
    """
    Classe modelo para API da Carteira de Criptomoedas
    """
    chave_api = models.CharField(null=True, max_length=128, verbose_name="Chave da API")
    chave_secreta = models.CharField(null=True, max_length=128,
                                     verbose_name="Chave Secreta da API")
    saldo = models.FloatField(null=False, verbose_name="Saldo a ser utilizado da carteira",
                              default=0.006)
    valor_operacao = models.FloatField(null=False, verbose_name="Valor de cada operação")
    num_operacoes = models.IntegerField(null=False, verbose_name="Número máximo de operações")
    simulacao = models.BooleanField(null=False, default=True, verbose_name="Modo de simulação")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )

    class Meta:
        db_table = 'carteiras'

    def __str__(self):
        return self.usuario.email

def pytradebot_json():
    """
    Metódo para gerar os valores padrão de configuração JSON do PyTradeBot
    """
    return {
        "max_open_trades": 3,
        "stake_currency": "BTC",
        "stake_amount": 0.05,
        "fiat_display_currency": "BRL",
        "ticker_interval" : "5m",
        "dry_run": True,
        "dry_run_wallet": 10,
        "trailing_stop": False,
        "stoploss": -0.10,
        "unfilledtimeout": {
            "buy": 10,
            "sell": 30
        },
        "bid_strategy": {
            "use_order_book": False,
            "ask_last_balance": 0.0,
            "order_book_top": 1,
            "check_depth_of_market": {
                "enabled": False,
                "bids_to_ask_delta": 1
            }
        },
        "ask_strategy":{
            "use_order_book": False,
            "order_book_min": 1,
            "order_book_max": 9,
            "use_sell_signal": True,
            "sell_profit_only": False,
            "ignore_roi_if_buy_signal": False
        },
        "pairlist": {
            "method": "VolumePairList",
            "config": {
                "number_assets": 20,
                "sort_key": "quoteVolume",
                "precision_filter": False
            }
        },
        "exchange": {
            "name": "binance",
            "key": "your_exchange_key",
            "secret": "your_exchange_secret",
            "ccxt_config": {"enableRateLimit": True},
            "ccxt_async_config": {
                "enableRateLimit": True,
                "rateLimit": 200
            },
            "pair_whitelist": [
            ],
            "pair_blacklist": [
                "BNB/BTC"
            ]
        },
        "edge": {
            "enabled": False,
            "process_throttle_secs": 3600,
            "calculate_since_number_of_days": 7,
            "capital_available_percentage": 0.5,
            "allowed_risk": 0.01,
            "stoploss_range_min": -0.01,
            "stoploss_range_max": -0.1,
            "stoploss_range_step": -0.01,
            "minimum_winrate": 0.60,
            "minimum_expectancy": 0.20,
            "min_trade_number": 10,
            "max_trade_duration_minute": 1440,
            "remove_pumps": False
        },
        "api_server": {
            "enabled": True,
            "listen_ip_address": "0.0.0.0",
            "listen_port": 8080,
            "username": "freqtrader",
            "password": "SuperSecurePassword"
        },
        "telegram": {
            "enabled": False,
            "token": "your_telegram_token",
            "chat_id": "your_telegram_chat_id"
        },
        "db_url": "postgresql+psycopg2://" + str(os.getenv('DB_USER')) + ":" \
                   + str(os.getenv('DB_PASSWORD')) + "@" + str(os.getenv('DB_HOST')) + ":" \
                   + str(os.getenv('DB_PORT')) + "/" + str(os.getenv('DB_NAME')),
        "initial_state": "running",
        "forcebuy_enable": True,
        "internals": {
            "process_throttle_secs": 5
        },
        "strategy": "DefaultStrategy",
        "strategy_path": "user_data/strategies/"
    }

class Usuario(AbstractUser):
    """
    Classe modelo do Usuário
    """
    username = None
    first_name = models.CharField(null=True, max_length=50, verbose_name="Nome")
    last_name = models.CharField(null=True, max_length=50, verbose_name="Sobrenome")
    cpf = BRCPFField(null=True, unique=True, max_length=14, verbose_name="CPF")
    telefone = models.CharField(null=True, max_length=14, verbose_name="Telefone")
    email = models.EmailField(null=False, unique=True, max_length=50, verbose_name="Email")
    password = models.CharField(null=False, max_length=128, verbose_name="Senha")
    is_active = models.BooleanField(null=False, default=True, verbose_name="Ativo")
    config_json = JSONField(verbose_name="Configurações JSON", default=pytradebot_json)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'cpf', 'telefone', 'password']

    objects = CustomUserManager()

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.email
