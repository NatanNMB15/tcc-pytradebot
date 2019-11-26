# Generated by Django 2.2.5 on 2019-11-19 20:15

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import mysite.models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='config_json',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=mysite.models.pytradebot_json, verbose_name='Configurações JSON'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.CharField(max_length=32, null=True, verbose_name='Exchange')),
                ('pair', models.CharField(max_length=32, null=True, verbose_name='Criptomoedas')),
                ('is_open', models.BooleanField(null=True, verbose_name='Ordem ativa')),
                ('fee_open', models.FloatField(null=True, verbose_name='Taxa de compra')),
                ('fee_close', models.FloatField(null=True, verbose_name='Taxa de venda')),
                ('open_rate', models.FloatField(null=True, verbose_name='Valor de compra')),
                ('open_rate_requested', models.FloatField(null=True, verbose_name='Valor de compra requisitado')),
                ('close_rate', models.FloatField(null=True, verbose_name='Valor de venda')),
                ('close_rate_requested', models.FloatField(null=True, verbose_name='Valor de venda requisitado')),
                ('close_profit', models.FloatField(null=True, verbose_name='Lucro realizado')),
                ('stake_amount', models.FloatField(null=True, verbose_name='Quantia máxima de compra')),
                ('amount', models.FloatField(null=True, verbose_name='Quantidade')),
                ('open_date', models.DateTimeField(null=True, verbose_name='Abertura')),
                ('close_date', models.DateTimeField(null=True, verbose_name='Fechamento')),
                ('open_order_id', models.CharField(max_length=128, null=True, verbose_name='ID da ordem')),
                ('stop_loss', models.FloatField(null=True, verbose_name='Valor stop-loss')),
                ('stop_loss_pct', models.FloatField(null=True, verbose_name='Porcentagem stop-loss')),
                ('initial_stop_loss', models.FloatField(null=True, verbose_name='Valor inicial stop-loss')),
                ('initial_stop_loss_pct', models.FloatField(null=True, verbose_name='Porcentagem                                                                        inicial stop-loss')),
                ('stoploss_order_id', models.CharField(max_length=128, null=True, verbose_name='ID stop-loss')),
                ('stoploss_last_update', models.DateTimeField(null=True, verbose_name='Última atualização de stop-loss')),
                ('max_rate', models.FloatField(null=True, verbose_name='Preço máximo')),
                ('min_rate', models.FloatField(null=True, verbose_name='Preço minímo')),
                ('sell_reason', models.CharField(max_length=128, null=True, verbose_name='Motivo de venda')),
                ('strategy', models.CharField(max_length=128, null=True, verbose_name='Estratégia')),
                ('ticker_interval', models.IntegerField(null=True, verbose_name='Intervalo de Tempo')),
                ('status_buy_sell', models.CharField(max_length=128, null=True, verbose_name='Status')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'db_table': 'trades',
            },
        ),
        migrations.CreateModel(
            name='CarteiraCriptomoeda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chave_api', models.CharField(max_length=128, null=True, verbose_name='Chave da API')),
                ('chave_secreta', models.CharField(max_length=128, null=True, verbose_name='Chave Secreta da API')),
                ('saldo', models.FloatField(null=True, verbose_name='Saldo da carteira')),
                ('valor_operacao', models.FloatField(verbose_name='Valor de cada operação')),
                ('num_operacoes', models.IntegerField(verbose_name='Número máximo de operações')),
                ('simulacao', models.BooleanField(default=True, verbose_name='Modo de simulação')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'db_table': 'carteiras',
            },
        ),
    ]
