# Generated by Django 2.2.2 on 2019-10-25 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_remove_newsletter_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='title',
            field=models.CharField(default=' ', max_length=50),
            preserve_default=False,
        ),
    ]
