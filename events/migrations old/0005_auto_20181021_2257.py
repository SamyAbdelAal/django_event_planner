# Generated by Django 2.1 on 2018-10-21 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_bookedevent_tickets'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='datetime',
        ),
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(default=-2007),
            preserve_default=False,
        ),
    ]
