from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth import get_user_model
from django.core.management import CommandError


class Command(createsuperuser.Command):
    """
    Classe para criar super usuário Django
    """
    help = 'Create a superuser, and allow password to be provided'

    def handle(self, *args, **options):
        password = options.get('password')
        email = options.get('email')
        database = options.get('database')

        user_model = get_user_model()
        user = user_model.objects.filter(email=email)

        if user.exists():
            print('Conta Admin já criada.')
        else:
            if not email:
                raise CommandError("O argumento --email é necessário.")
            if not password:
                raise CommandError("O argumento --password é necessário.")
            user_model.objects.create_superuser(email, password)
