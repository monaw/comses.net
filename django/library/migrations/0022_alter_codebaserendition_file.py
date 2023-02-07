# Generated by Django 3.2.17 on 2023-02-07 04:02

from django.db import migrations
import wagtail.images.models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0021_auto_20221003_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codebaserendition',
            name='file',
            field=wagtail.images.models.WagtailImageField(height_field='height', upload_to=wagtail.images.models.get_rendition_upload_to, width_field='width'),
        ),
    ]
