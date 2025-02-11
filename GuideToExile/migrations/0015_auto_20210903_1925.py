# Generated by Django 3.2.6 on 2021-09-03 17:25

from django.db import migrations

from GuideToExile.models import AscendancyClass


def export_asc_classes(apps, schema_editor):
    asc_name_mapping = {i.label: i.value for i in AscendancyClass.AscClassName}
    base_name_mapping = {i.label: i.value for i in AscendancyClass.BaseClassName}
    AscClass = apps.get_model('GuideToExile', 'AscendancyClass')
    for asc_class in AscClass.objects.all():
        asc_name = asc_class.name
        base_name = asc_class.base_class_name
        asc_class._name = asc_name_mapping[asc_name]
        asc_class._base_class_name = base_name_mapping[base_name]
        asc_class.save()


def revert_export_asc_classes(apps, schema_editor):
    AscendancyClass = apps.get_model('GuideToExile', 'AscendancyClass')


class Migration(migrations.Migration):
    dependencies = [
        ('GuideToExile', '0014_auto_20210903_1925'),
    ]

    operations = [
        migrations.RunPython(export_asc_classes, revert_export_asc_classes)
    ]
