# Generated by Django 2.1 on 2018-10-21 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20181021_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(blank=True, default=123456, null=True),
        ),
    ]