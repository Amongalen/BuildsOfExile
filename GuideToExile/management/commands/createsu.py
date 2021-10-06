import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    username = os.environ['SU_USERNAME']
    password = os.environ['SU_PASSWORD']
    email = os.environ['SU_EMAIL']

    def handle(self, *args, **options):
        if not get_user_model().objects.filter(username=self.username).exists():
            get_user_model().objects.create_superuser(self.username, self.email, self.password)
