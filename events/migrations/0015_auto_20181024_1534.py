# Generated by Django 2.1 on 2018-10-24 12:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0014_auto_20181024_1511'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follower',
            unique_together={('follower', 'followed')},
        ),
    ]