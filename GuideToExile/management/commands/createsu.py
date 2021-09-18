import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    username = os.environ['SU_USERNAME']
    password = os.environ['SU_PASSWORD']
    email = os.environ['SU_EMAIL']

    def handle(self, *args, **options):
        if not User.objects.filter(username=self.username).exists():
            User.objects.create_superuser(self.username, self.email, self.password)
