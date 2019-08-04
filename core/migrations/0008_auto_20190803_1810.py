# Generated by Django 2.2.2 on 2019-08-03 17:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_auto_20190803_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='PaymentOptions',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='payment_options',
            field=models.ManyToManyField(related_name='payment_method', to='core.PaymentOptions'),
        ),
    ]
