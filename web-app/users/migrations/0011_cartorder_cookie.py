# Generated by Django 4.2.9 on 2024-04-25 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_order_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorder',
            name='cookie',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
