class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0003_auto_20200515_1309"),
        ("global_config", "0010_auto_20200623_1222"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Change_Actual",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("Change_Initiation_Date", models.DateTimeField(verbose_name="Change Start Date")),
                ("Change_Description", models.TextField(verbose_name="Change Description")),
                (
                    "Change_Risk_Assesment",
                    models.TextField(verbose_name="Risk Assessment and Mitigation"),
                ),
                ("Cut_In_Number", models.CharField(max_length=200, verbose_name="Cut In Number")),
                (
                    "Cut_Out_Number",
                    models.CharField(max_length=200, verbose_name="Cut Out Number"),
                ),
                (
                    "Change_Initiator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Change Initiator",
                    ),
                ),
            ],
        ),
    ]


class NotAMigration(migrations.Migration):
    initial = True


    dependencies = [
        ("users", "0003_auto_20200515_1309"),
        ("global_config", "0010_auto_20200623_1222"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Do_Not_Find_Me",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("Change_Initiation_Date", models.DateTimeField(verbose_name="Change Start Date")),
                ("Change_Description", models.TextField(verbose_name="Change Description")),
                (
                    "Change_Risk_Assesment",
                    models.TextField(verbose_name="Risk Assessment and Mitigation"),
                ),
                ("Cut_In_Number", models.CharField(max_length=200, verbose_name="Cut In Number")),
                (
                    "Cut_Out_Number",
                    models.CharField(max_length=200, verbose_name="Cut Out Number"),
                ),
                (
                    "Change_Initiator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Change Initiator",
                    ),
                ),
            ],
        ),
    ]