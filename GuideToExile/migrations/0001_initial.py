# Generated by Django 3.2.6 on 2021-08-19 19:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import GuideToExile.json_encoder


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Keystone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UniqueItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=150)),
                ('bio', models.TextField()),
                ('signup_confirmation', models.BooleanField(default=False)),
                ('user',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BuildGuide',
            fields=[
                ('build_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('pob_string', models.CharField(max_length=40000)),
                ('pob_details', models.JSONField(decoder=GuideToExile.json_encoder.BuildDetailsJsonDecoder,
                                                 encoder=GuideToExile.json_encoder.BuildDetailsJsonEncoder)),
                ('title', models.CharField(max_length=255)),
                ('text', models.CharField(max_length=40000)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                             to='GuideToExile.userprofile')),
                ('keystones',
                 models.ManyToManyField(related_name='keystones_related_builds', to='GuideToExile.Keystone')),
                ('unique_items',
                 models.ManyToManyField(related_name='unique_items_related_builds', to='GuideToExile.UniqueItem')),
            ],
        ),
    ]
