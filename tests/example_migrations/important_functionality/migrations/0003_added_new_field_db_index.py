# -*- coding: utf-8 -*-

# Django
from django.db import migrations
from django.db import models


def load_data(apps, schema_editor):
    SiteType = apps.get_model("core", "SiteType")
    SiteType(id=4, name="basic").save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="site_type",
            field=models.ForeignKey(
                related_name="sites",
                to="core.SiteType",
                help_text="Type of this site (primary/nursery/basic)",
                on_delete=models.CASCADE,
            ),
        ),
        migrations.RunPython(load_data),
    ]
