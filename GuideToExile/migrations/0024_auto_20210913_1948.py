# Generated by Django 3.2.6 on 2021-09-13 17:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('GuideToExile', '0023_auto_20210913_1822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buildguide',
            name='is_archived',
        ),
        migrations.RemoveField(
            model_name='buildguide',
            name='is_published',
        ),
        migrations.AddField(
            model_name='buildguide',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'draft'), (2, 'published'), (3, 'archived')],
                                                   default=2),
            preserve_default=False,
        ),
    ]
