# Generated by Django 4.1.3 on 2023-01-21 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="tusmk_id",
            field=models.CharField(max_length=60, null=True),
        ),
    ]
