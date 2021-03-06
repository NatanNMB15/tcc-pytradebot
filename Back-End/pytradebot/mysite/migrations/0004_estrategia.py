# Generated by Django 2.2.5 on 2019-12-02 18:54

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0003_auto_20191126_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estrategia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=128, verbose_name='Nome da Estratégia')),
                ('template', models.CharField(max_length=128, null=True, verbose_name='Template da Estratégia')),
                ('metricas', django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='Métricas JSON')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'db_table': 'estrategias',
            },
        ),
    ]
