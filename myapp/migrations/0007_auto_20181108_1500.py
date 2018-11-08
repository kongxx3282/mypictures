# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-08 07:00
from __future__ import unicode_literals

from django.db import migrations, models
import system.storage


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_auto_20181104_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='version',
            name='digital_picture',
            field=models.ImageField(storage=system.storage.ImageStorage(), upload_to='digitalmark'),
        ),
        migrations.AlterField(
            model_name='version',
            name='original_picture',
            field=models.ImageField(storage=system.storage.ImageStorage(), upload_to='original'),
        ),
        migrations.AlterField(
            model_name='version',
            name='watermark_picture',
            field=models.ImageField(storage=system.storage.ImageStorage(), upload_to='watermark'),
        ),
    ]
