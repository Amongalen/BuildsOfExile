# Generated by Django 3.2.6 on 2021-09-21 18:49

from django.db import migrations

import GuideToExile.models


class Migration(migrations.Migration):
    dependencies = [
        ('GuideToExile', '0029_rename_user_table'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', GuideToExile.models.CustomUserManager()),
            ],
        ),
    ]
