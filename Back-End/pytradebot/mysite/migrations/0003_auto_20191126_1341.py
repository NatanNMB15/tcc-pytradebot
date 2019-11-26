from django.conf import settings
from django.db import migrations


def update_site_domain(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    s, _ = Site.objects.get_or_create(pk=settings.SITE_ID)
    s.domain = str(settings.HOST)
    s.name = str(settings.HOST)
    s.save()


class Migration(migrations.Migration):

    dependencies = [
        ("mysite", "0003_auto_20191121_1650"),
        ("sites", "0002_alter_domain_unique"),  # highest-numbered migration for the sites framework
    ]

    operations = [migrations.RunPython(update_site_domain)]