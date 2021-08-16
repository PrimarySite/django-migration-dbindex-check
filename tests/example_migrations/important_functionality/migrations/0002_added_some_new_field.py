# -*- coding: utf-8 -*-

# Django
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="subdomain",
            field=models.CharField(
                help_text="Forms part of the web address for the editor view. For example, if set to 'stjosephs', the page editor will be available at 'stjosephs.[domain]'; where [domain] is the CMS base domain.",
                max_length=255,
                unique=True,
                null=True,
                verbose_name="Subdomain (internal)",
            ),
        ),
    ]
