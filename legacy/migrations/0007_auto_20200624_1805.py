# Generated by Django 2.0.13 on 2020-06-24 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legacy', '0006_auto_20200602_1318'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diagnostictesting',
            old_name='antihistimines',
            new_name='antihistamines',
        ),
    ]
