# Generated by Django 2.1 on 2018-10-23 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, max_length=300),
        ),
    ]
