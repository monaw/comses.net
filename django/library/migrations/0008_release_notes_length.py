# Generated by Django 2.2.1 on 2019-05-07 23:10

import core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_rename_platform_to_operating_system'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codebaserelease',
            name='release_notes',
            field=core.fields.MarkdownField(blank=True, help_text='Markdown formattable text, e.g., run conditions', max_length=2048, rendered_field=True),
        ),
        migrations.AlterField(
            model_name='codebaserelease',
            name='summary',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
