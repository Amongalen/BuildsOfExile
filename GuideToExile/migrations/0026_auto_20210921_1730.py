# Generated by Django 3.2.6 on 2021-09-21 15:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('GuideToExile', '0025_alter_buildguide_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildguide',
            name='text',
            field=models.CharField(max_length=40000, null=True),
        ),
        migrations.AlterField(
            model_name='buildguide',
            name='title',
            field=models.CharField(max_length=180, null=True),
        ),
    ]
