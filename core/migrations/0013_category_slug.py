# Generated by Django 2.2.8 on 2020-02-20 12:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20200213_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]