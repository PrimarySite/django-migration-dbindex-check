# Generated by Django 2.0.13 on 2020-07-02 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("change_management", "0002_auto_20200701_1444"),
    ]

    operations = [
        migrations.AddField(
            model_name="change_status",
            name="All_Signatures_Required",
            field=models.BooleanField(
                default=False,
                verbose_name="Are all signatures required for this status to be active?",
            ),
            db_index=True,
        ),
    ]
