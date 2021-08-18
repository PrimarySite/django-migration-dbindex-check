# Generated by Django 2.0.13 on 2020-07-01 12:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0003_auto_20200515_1309"),
        ("global_config", "0010_auto_20200623_1222"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="Change_Actual",
            name="MadeUpField",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="wonde.WondeAccount",
                db_index=True,
            ),
        ),
    ]