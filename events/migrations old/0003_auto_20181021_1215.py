# Generated by Django 2.1 on 2018-10-21 09:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0002_auto_20181021_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookedEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='favoriteevent',
            name='event',
        ),
        migrations.RemoveField(
            model_name='favoriteevent',
            name='user',
        ),
        migrations.RemoveField(
            model_name='event',
            name='logo',
        ),
        migrations.DeleteModel(
            name='FavoriteEvent',
        ),
        migrations.AddField(
            model_name='bookedevent',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
        ),
        migrations.AddField(
            model_name='bookedevent',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
