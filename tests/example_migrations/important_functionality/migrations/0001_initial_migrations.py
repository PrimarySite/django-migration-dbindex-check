# -*- coding: utf-8 -*-

# Standard Library
import datetime

# Project
import core.db.fields
import core.models
import core.utils.file_storage
# Django
import django.core.files.storage
import django.db.models.deletion
# 3rd-party
import storages.backends.s3boto
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("twitter", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityStreamIntroText",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "typename",
                    models.CharField(
                        max_length=16,
                        choices=[
                            ("newsitem", "News"),
                            ("newsletteritem", "Newsletter"),
                        ],
                    ),
                ),
                ("content", models.TextField(default="", blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="ActivityStreamProxy",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("object_id", models.PositiveIntegerField(db_index=True)),
                ("title", models.CharField(max_length=1024)),
                ("summary", models.TextField(default="", blank=True)),
                ("content", models.TextField(default="", blank=True)),
                ("plain_content", models.TextField(default="", blank=True)),
                ("secondary_sort", models.IntegerField(default=0)),
                ("date", models.DateTimeField()),
                ("proxy_text", models.TextField(default="", blank=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        to="contenttypes.ContentType", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"ordering": ("-date", "-secondary_sort"),},
        ),
        migrations.CreateModel(
            name="BaseSlug",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="A permanent slug to be used in templates: it doesn't change if the page title changes.",
                        max_length=255,
                        verbose_name="Base slug",
                    ),
                ),
                (
                    "gid",
                    models.CharField(
                        help_text="The gid that corresponds to the base slug. This should be updated when moving the theme to another environment.",
                        max_length=255,
                        verbose_name="GID",
                        db_index=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CalendarCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "colour",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, "light-blue"),
                            (2, "dark-blue"),
                            (3, "light-green"),
                            (4, "dark-green"),
                            (5, "orange"),
                            (6, "red"),
                            (7, "purple"),
                            (8, "dark-purple"),
                            (9, "grey"),
                            (10, "dark-grey"),
                        ],
                    ),
                ),
                ("title", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="DiaryEntry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("title", models.TextField(default="")),
                ("body", models.TextField(default="", blank=True)),
                ("start", models.DateTimeField()),
                ("start_all_day", models.BooleanField(default=True)),
                ("end", models.DateTimeField(null=True)),
                ("end_all_day", models.BooleanField(default=True)),
                ("background", models.BooleanField(default=False)),
                (
                    "event_colour",
                    models.CharField(
                        default="light-blue",
                        help_text="The colour used for an event",
                        max_length=20,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Automatically based on the name of the topic",
                        null=True,
                        verbose_name="Slug",
                    ),
                ),
            ],
            options={"ordering": ("start",),},
        ),
        migrations.CreateModel(
            name="DiaryOccurrence",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("date", models.DateTimeField()),
                ("is_start", models.BooleanField(default=False)),
                ("is_end", models.BooleanField(default=False)),
                (
                    "entry",
                    models.ForeignKey(to="core.DiaryEntry", on_delete=models.CASCADE),
                ),
            ],
            options={"ordering": ["date"],},
        ),
        migrations.CreateModel(
            name="EventCategories",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("order", models.IntegerField()),
                (
                    "calendar_category",
                    models.ForeignKey(
                        to="core.CalendarCategory", on_delete=models.CASCADE
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(to="core.DiaryEntry", on_delete=models.CASCADE),
                ),
            ],
            options={"verbose_name_plural": "Event categories",},
        ),
        migrations.CreateModel(
            name="FreeSnippet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=1024, verbose_name="Name")),
                (
                    "content",
                    models.CharField(
                        max_length=1024, verbose_name="Content", blank=True
                    ),
                ),
                (
                    "identifier",
                    models.SlugField(
                        blank=True,
                        help_text="An identifier that themers can use.",
                        null=True,
                        verbose_name="Slug for use by themers",
                    ),
                ),
                (
                    "template",
                    models.CharField(
                        default="core.homepage.html",
                        choices=[("core.homepage.html", "core.homepage.html")],
                        max_length=1024,
                        blank=True,
                        help_text="The template where it is expected that this snippet will be used. The snippet may be used in other pages, but the snippet may only be edited from this page.",
                        null=True,
                        verbose_name="Template file this is expected to be used in. Not compulsory.",
                    ),
                ),
                (
                    "name_from_templatetag",
                    models.BooleanField(
                        default=False,
                        help_text="If it's true then the snippet name can be changed from the templates only, and not from the admin interface.",
                    ),
                ),
            ],
            options={"verbose_name": "Home Page Snippet",},
        ),
        migrations.CreateModel(
            name="InfoBarMessage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("message", models.CharField(default="", max_length=1024)),
                ("start", models.DateTimeField(default=datetime.datetime.now)),
                ("end", models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="NewsItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("title", models.CharField(max_length=1024)),
                ("deleted", models.BooleanField(default=False)),
                ("draft", models.BooleanField(default=True)),
                ("author", models.CharField(max_length=1024, blank=True)),
                ("content", models.TextField(default="", blank=True)),
                ("plain_content", models.TextField(default="", blank=True)),
                ("date", models.DateField()),
                (
                    "pictures_content",
                    core.db.fields.JSONField(default=dict, null=True, blank=True),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Automatically set based on the page title and changes in line with the page title.",
                        null=True,
                        verbose_name="Slug, or path component for this news item",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="NewsletterItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("title", models.CharField(max_length=1024)),
                ("date", models.DateField()),
                ("deleted", models.BooleanField(default=False)),
                (
                    "uploaded_files",
                    core.db.fields.JSONField(default=dict, null=True, blank=True),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Automatically set based on the page title and changes in line with the page title.",
                        null=True,
                        verbose_name="Slug, or path component for this news item",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("title", models.CharField(max_length=255)),
                (
                    "gid",
                    core.db.fields.UUIDField(db_index=True, max_length=64, blank=True),
                ),
                (
                    "content",
                    core.db.fields.JSONField(default=dict, null=True, blank=True),
                ),
                (
                    "layout_identifier",
                    models.CharField(
                        help_text="Names the style of layout in use",
                        max_length=255,
                        null=True,
                        blank=True,
                    ),
                ),
                ("top_id", models.IntegerField(default=0)),
                (
                    "page_layout",
                    core.db.fields.JSONField(default=dict, null=True, blank=True),
                ),
                (
                    "_rendered",
                    models.TextField(
                        default="", null=True, db_column="rendered", blank=True
                    ),
                ),
                ("processed_by_script", models.NullBooleanField(default=False)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PageMeta",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "redirect_to",
                    models.CharField(
                        default="",
                        help_text="Relative URL to link, starting with '/' OR\n                  redirect to calendar_grid enter: 'calendar_grid'.",
                        max_length=512,
                        blank=True,
                    ),
                ),
                (
                    "gid",
                    models.CharField(
                        max_length=255, unique=True, null=True, db_index=True
                    ),
                ),
                (
                    "access_permissions",
                    core.db.fields.JSONField(
                        default=dict,
                        help_text="Raw JSON representation of access permissions",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "parent_page",
                    models.CharField(
                        default="", max_length=255, db_index=True, blank=True
                    ),
                ),
                (
                    "parent_topic",
                    models.CharField(
                        default="", max_length=255, db_index=True, blank=True
                    ),
                ),
                (
                    "page_order",
                    models.IntegerField(
                        default=0, help_text="Order page comes in its relevant Topic"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=255,
                        blank=True,
                        help_text="Automatically set based on the page title and\n            changes in line with the page title",
                        null=True,
                        verbose_name="Slug, or path component for this page",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "image_privatisation_in_queue",
                    models.BooleanField(
                        default=False, verbose_name="Queued to change privatisation"
                    ),
                ),
                (
                    "draft_version",
                    models.ForeignKey(
                        related_name="draft",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="core.Page",
                        null=True,
                    ),
                ),
                (
                    "head_version",
                    models.ForeignKey(
                        related_name="head", to="core.Page", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"ordering": ("page_order", "id"),},
        ),
        migrations.CreateModel(
            name="PagePromotion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "page_gid",
                    models.CharField(
                        db_index=True,
                        max_length=255,
                        unique=True,
                        null=True,
                        blank=True,
                    ),
                ),
                ("date", models.DateField(auto_now_add=True)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PageRefPage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("from_page", models.CharField(max_length=255)),
                ("to_page", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("name", models.CharField(max_length=255, verbose_name="School name")),
                (
                    "postcode",
                    models.CharField(default="", max_length=8, null=True, blank=True),
                ),
                (
                    "urn",
                    models.CharField(default="", max_length=8, null=True, blank=True),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="SchoolUserRole",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("deleted", models.BooleanField(default=False)),
                (
                    "role",
                    models.IntegerField(
                        help_text="The type of role this represents",
                        choices=[
                            (4, "Superuser"),
                            (2, "Teacher"),
                            (5, "Teaching Assistant"),
                            (3, "Governor"),
                            (6, "Governor (read-only)"),
                            (7, "Office"),
                            (8, "PTA"),
                            (9, "Inspector (e.g. Ofsted)"),
                            (10, "Parent"),
                            (11, "Pupil"),
                        ],
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        related_name="roles",
                        to="core.School",
                        help_text="School this Role is associated with",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("name", models.CharField(max_length=255, verbose_name="Site name")),
                (
                    "subdomain",
                    models.CharField(
                        help_text="Forms part of the web address for the editor view. For example, if set to 'stjosephs', the page editor will be available at 'stjosephs.primarysite.local'",
                        max_length=255,
                        unique=True,
                        null=True,
                        verbose_name="Subdomain (internal)",
                    ),
                ),
                (
                    "media_right_click_disabled",
                    models.BooleanField(
                        default=True,
                        help_text="When this is selected, a menu no longer apears when right clicking on media elements (video and images) to stop users from accessing the context menu and saving media.",
                    ),
                ),
                (
                    "maintenance_mode",
                    models.BooleanField(
                        default=True,
                        help_text="When in maintenance mode, the site is not publicly  accessible - instead a holding page will be shown",
                    ),
                ),
                (
                    "width",
                    models.IntegerField(
                        verbose_name="Overall content-area width for Content Pages in this site"
                    ),
                ),
                (
                    "news_width",
                    models.IntegerField(
                        help_text="Set this to narrower than the site's width if a Theme template uses a sidebar with links, for example, to avoid image slideshows being rendered wider than the available space",
                        verbose_name="Overall content-area width for News stories in this site",
                    ),
                ),
                (
                    "background_colour",
                    models.CharField(
                        help_text="Background colour to use in editor when editing page content",
                        max_length=128,
                    ),
                ),
                (
                    "simple_mode",
                    models.BooleanField(
                        default=True,
                        help_text="Unticking this box will enable advanced editor controls, which reveals the draft-mode functionality to the CMS user",
                        verbose_name="Show 'Simple' editor controls",
                    ),
                ),
                (
                    "access_permissions",
                    core.db.fields.JSONField(
                        default='{"1": [], "2": [7], "3": [7], "4": [1, 2, 3, 5, 4, 6, 7], "5": [7], "6": [7], "7": [2, 3, 4, 5, 6, 7], "8": [7], "9": [7], "10": [], "11": []}',
                        help_text="Raw JSON representation of site-wide access permissions. Not intended for manual editing",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "page_structure",
                    models.TextField(
                        default="\nAbout Us\\about-us||Welcome\nAbout Us\\about-us||Visions and Values\nAbout Us\\about-us||Contact Details\nAbout Us\\about-us||Who's Who\nAbout Us\\about-us||Virtual School Tour**/special/virtual-tour/\nAbout Us\\about-us||Governors\nAbout Us\\about-us||Staff Zone\nAbout Us\\about-us||Governors' Zone\nAbout Us\\about-us||Vacancies\nKey Information\\key-information||Curriculum||English\nKey Information\\key-information||Curriculum||Maths\nKey Information\\key-information||Curriculum||Science\nKey Information\\key-information||Curriculum||History\nKey Information\\key-information||Admissions\nKey Information\\key-information||Ofsted Reports\nKey Information\\key-information||Pupil Premium\nKey Information\\key-information||Policies\nNews and Events\\news-and-events||Latest News**/stream/news/full/1/-//\nNews and Events\\news-and-events||Calendar**calendar_grid\nNews and Events\\news-and-events||Newsletters**/stream/newsletters/full/1/-//\nParents\\parents||Useful Information\nParents\\parents||School Clubs||Football\nParents\\parents||School Clubs||Dance\nParents\\parents||School Clubs||Gymnastics\nParents\\parents||School Clubs||Chess\nParents\\parents||PTA\nParents\\parents||Useful Links\nChildren\\children||Class Pages||Foundation\nChildren\\children||Class Pages||Reception\nChildren\\children||Class Pages||Class 1\nChildren\\children||Class Pages||Class 2\nChildren\\children||Class Pages||Class 3\nChildren\\children||Class Pages||Class 4\nChildren\\children||Class Pages||Class 5\nChildren\\children||Class Pages||Class 6\nChildren\\children||Kids' Zone**/special/kidszone/\nChildren\\children||Gallery\nChildren\\children||Blogging**http://school.primaryblog.net\nChildren\\children||Podcasting**http://school.primarypodcast.com\nChildren\\children||House Pages||Red House\nChildren\\children||House Pages||Blue House\nChildren\\children||House Pages||Yellow House\nChildren\\children||House Pages||Green House\n",
                        blank=True,
                    ),
                ),
                (
                    "can_edit_ckeditor_source",
                    models.BooleanField(
                        default=False,
                        help_text="Ticking this box will give editors access to the HTML 'Source' button when editing richtext blocks and news items",
                        verbose_name="Show the CKEditor source button",
                    ),
                ),
                (
                    "can_enable_seasonal_effects",
                    models.BooleanField(
                        default=False,
                        help_text="Permit the school to add falling snow effects (for example) on the home page",
                    ),
                ),
                ("seasonal_effect_active", models.BooleanField(default=False)),
                (
                    "seasonal_effect_type",
                    models.IntegerField(
                        default=3,
                        blank=True,
                        choices=[
                            (1, "Autumn Leaves"),
                            (9, "Chinese New Year"),
                            (4, "Christmas"),
                            (10, "Diwali"),
                            (7, "Easter"),
                            (11, "Eid"),
                            (17, "Footballs"),
                            (2, "Hallowe'en"),
                            (12, "Hanukkah"),
                            (18, "Remembrance Day"),
                            (19, "Shrove Tuesday"),
                            (3, "Snow"),
                            (21, "Sports Day"),
                            (13, "Spring"),
                            (16, "St Andrew's Day"),
                            (14, "St David's Day"),
                            (15, "St George's Day"),
                            (6, "St Patrick's Day"),
                            (8, "Stars"),
                            (22, "Summer"),
                            (20, "Tennis"),
                            (5, "Valentine's Day"),
                        ],
                    ),
                ),
                ("piwik_site_id", models.IntegerField(null=True, blank=True)),
                (
                    "previous_url",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "regen_images_in_queue",
                    models.BooleanField(
                        default=False,
                        help_text="This indicates if there is currently a celery task queued for changing the size of regular images",
                        verbose_name="Regular images are queued to be resized",
                    ),
                ),
                (
                    "regen_news_images_in_queue",
                    models.BooleanField(
                        default=False,
                        help_text="This indicates if there is currently a celery task queued for changing the size of news images",
                        verbose_name="News images are queued to be resized",
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        related_name="sites",
                        to="core.School",
                        help_text="School with which this site is associated",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="SiteDomain",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="A root URL at which the site will be publicly available - eg: https://www.exampleschool.com/",
                        unique=True,
                        verbose_name="Site domain root URL",
                    ),
                ),
                (
                    "canonical",
                    models.BooleanField(
                        default=False,
                        help_text="This is the canonical (ie, main) domain for the site in question. There MUST be one and only one canonical domain for each Site",
                    ),
                ),
                ("site", models.ForeignKey(to="core.Site", on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name="SiteImageAsset",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SiteType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=31, verbose_name="Type name")),
            ],
        ),
        migrations.CreateModel(
            name="Slideshow",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=1024, verbose_name="Name")),
                (
                    "identifier",
                    models.SlugField(
                        blank=True,
                        help_text="An identifier that themers can use.",
                        null=True,
                        verbose_name="Slug for use by themers",
                    ),
                ),
                (
                    "template",
                    models.CharField(
                        default="core.homepage.html",
                        choices=[("core.homepage.html", "core.homepage.html")],
                        max_length=1024,
                        blank=True,
                        help_text="The template where it is expected that this snippet will be used. The snippet may be used in other pages, but the snippet may only be edited from this page.",
                        null=True,
                        verbose_name="Template file this is expected to be used in. Not compulsory.",
                    ),
                ),
                (
                    "pictures_content",
                    core.db.fields.JSONField(default=dict, null=True, blank=True),
                ),
                (
                    "max_picture_count",
                    models.IntegerField(
                        default=8,
                        help_text="The maximum number of images that will be displayed in this slideshow",
                    ),
                ),
                (
                    "name_from_templatetag",
                    models.BooleanField(
                        default=False,
                        help_text="If it's true then the snippet name can be changed from the templates only, and not from the admin interface.",
                    ),
                ),
                (
                    "is_fullscreen",
                    models.BooleanField(
                        default=False,
                        help_text="If yes, the slideshow will become fullscreen",
                    ),
                ),
                ("site", models.ForeignKey(to="core.Site", on_delete=models.CASCADE)),
            ],
            options={"ordering": ["name"],},
        ),
        migrations.CreateModel(
            name="Theme",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name for this theme.",
                        unique=True,
                        max_length=1024,
                        verbose_name="Theme Name",
                    ),
                ),
                (
                    "added_to_portfolio",
                    models.DateField(
                        help_text="When was this added to the primarysite.net pre-design portfolio?",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        verbose_name="Theme Owner",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "theme_parent",
                    models.ForeignKey(
                        related_name="theme_children",
                        blank=True,
                        to="core.Theme",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ["name"],},
        ),
        migrations.CreateModel(
            name="ThemeAssetFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the file.",
                        max_length=2048,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "asset_file",
                    models.FileField(
                        storage=storages.backends.s3boto.S3BotoStorage(
                            bucket="primarysite-local-dev"
                        ),
                        max_length=512,
                        upload_to=core.models._upload_to_name,
                    ),
                ),
                (
                    "content_type",
                    models.CharField(
                        max_length=512,
                        verbose_name="The MIME type of the object",
                        blank=True,
                    ),
                ),
                (
                    "theme",
                    models.ForeignKey(
                        help_text="The Theme that this file comprises.",
                        to="core.Theme",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ThemeEditorStyle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "theme",
                    models.IntegerField(
                        choices=[(1, "default"), (2, "pastel-on-dark")]
                    ),
                ),
            ],
            options={"ordering": ["name"],},
        ),
        migrations.CreateModel(
            name="ThemeTemplate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the template, so it can be extended or included.",
                        max_length=512,
                        verbose_name="Template name",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text="The Template content, in Django template format.",
                        blank=True,
                    ),
                ),
                (
                    "theme",
                    models.ForeignKey(
                        help_text="The Theme that this Template comprises.",
                        to="core.Theme",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ["name"],},
        ),
        migrations.CreateModel(
            name="ThemeTextFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the file, so it can be included.",
                        max_length=2048,
                        verbose_name="Filename",
                    ),
                ),
                (
                    "content_type",
                    models.IntegerField(
                        verbose_name="The MIME type of the object",
                        choices=[
                            (1, "text/css"),
                            (2, "application/javascript"),
                            (3, "text/plain"),
                        ],
                    ),
                ),
                (
                    "content",
                    models.TextField(verbose_name="The text content of the file"),
                ),
                (
                    "s3_url",
                    models.CharField(
                        help_text="The URL of the file in S3.",
                        max_length=512,
                        verbose_name="S3Url",
                        blank=True,
                    ),
                ),
                (
                    "theme",
                    models.ForeignKey(
                        help_text="The Theme that this file comprises.",
                        to="core.Theme",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ThemeType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name for theme type",
                        unique=True,
                        max_length=512,
                        verbose_name="Theme type name",
                    ),
                ),
                (
                    "is_master",
                    models.BooleanField(help_text="Is theme type is a master one"),
                ),
                ("is_public", models.BooleanField()),
                ("order", models.IntegerField()),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        to="core.ThemeType",
                        help_text="Parent theme type for",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ["order"],},
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                (
                    "gid",
                    core.db.fields.UUIDField(
                        db_index=True, unique=True, max_length=64, blank=True
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Automatically based on the name of the topic",
                        null=True,
                        verbose_name="Slug, or path component for this topic",
                    ),
                ),
                (
                    "name_from_templatetag",
                    models.BooleanField(
                        default=False,
                        help_text="If it's true then the snippet name can be changed from the templates only, and not from the admin interface.",
                    ),
                ),
                ("site", models.ForeignKey(to="core.Site", on_delete=models.CASCADE)),
            ],
            options={"ordering": ("name",),},
        ),
        migrations.CreateModel(
            name="UploadedAudio",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "containing_page_gid",
                    core.db.fields.UUIDField(max_length=64, null=True, blank=True),
                ),
                (
                    "gid",
                    core.db.fields.UUIDField(db_index=True, max_length=64, blank=True),
                ),
                ("asset_moved", models.BooleanField(default=False)),
                ("asset_move_failed", models.BooleanField(default=False)),
                (
                    "filedata",
                    models.FileField(
                        storage=django.core.files.storage.FileSystemStorage(
                            location="/home/vagrant/primarysite/static"
                        ),
                        upload_to=core.utils.file_storage.generate_path_original_filename,
                        max_length=512,
                        verbose_name="Source file provided",
                    ),
                ),
                (
                    "filedata_remote",
                    models.FileField(
                        upload_to=core.utils.file_storage.generate_path_original_filename,
                        max_length=512,
                        blank=True,
                        null=True,
                        verbose_name="Source file provided, remote",
                        db_index=True,
                    ),
                ),
                (
                    "pending_encoding",
                    models.BooleanField(
                        default=False,
                        help_text="If True, this asset has been submitted for encoding, but has not yet been completed",
                    ),
                ),
                (
                    "job_failed",
                    models.BooleanField(
                        default=False,
                        help_text="If True, the asset has been submitted for encoding, but the encoding job failed",
                    ),
                ),
                (
                    "last_encoding_job_id",
                    models.CharField(
                        help_text="This is the job ID reference for the last time the asset was submitted to the encoding service. If blank, it means the job has never been submitted. If non-blank, check the status of pending_encoding",
                        max_length=32,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "needs_reencoding",
                    models.BooleanField(
                        default=False,
                        help_text="Tick this if, for some reason, the converted clip needs re-converting from source'",
                        editable=False,
                    ),
                ),
                (
                    "duration_ms",
                    models.IntegerField(
                        help_text="Duration, in milliseconds, based on Zencoder's output",
                        null=True,
                        blank=True,
                    ),
                ),
                ("uploaded_on", models.DateTimeField(auto_now_add=True)),
                (
                    "output_mp3_cloud_uri",
                    models.CharField(
                        help_text="The address of the converted MP4 file in the Amazon S3 'bucket'",
                        max_length=2000,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "output_mp3_cloud_size",
                    models.IntegerField(
                        help_text="Size, in bytes", null=True, blank=True
                    ),
                ),
                (
                    "page_meta",
                    models.ForeignKey(
                        related_name="core_uploadedaudio_uploads",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.PageMeta",
                        null=True,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        related_name="core_uploadedaudio_site",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.Site",
                        null=True,
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="UploadedDocument",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "containing_page_gid",
                    core.db.fields.UUIDField(max_length=64, null=True, blank=True),
                ),
                (
                    "gid",
                    core.db.fields.UUIDField(db_index=True, max_length=64, blank=True),
                ),
                ("asset_moved", models.BooleanField(default=False)),
                ("asset_move_failed", models.BooleanField(default=False)),
                (
                    "filedata",
                    models.FileField(
                        max_length=512,
                        upload_to=core.utils.file_storage.generate_path_original_filename,
                    ),
                ),
                ("uploaded_on", models.DateTimeField(auto_now_add=True)),
                (
                    "page_meta",
                    models.ForeignKey(
                        related_name="core_uploadeddocument_uploads",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.PageMeta",
                        null=True,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        related_name="core_uploadeddocument_site",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.Site",
                        null=True,
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="UploadedImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "containing_page_gid",
                    core.db.fields.UUIDField(max_length=64, null=True, blank=True),
                ),
                (
                    "gid",
                    core.db.fields.UUIDField(db_index=True, max_length=64, blank=True),
                ),
                ("asset_moved", models.BooleanField(default=False)),
                ("asset_move_failed", models.BooleanField(default=False)),
                (
                    "filedata",
                    models.ImageField(
                        upload_to=core.utils.file_storage.generate_path_and_unique_filename,
                        max_length=512,
                        verbose_name="Original file data",
                    ),
                ),
                ("uploaded_on", models.DateTimeField(auto_now_add=True)),
                ("full_width_image_width", models.IntegerField(null=True, blank=True)),
                ("full_width_image_height", models.IntegerField(null=True, blank=True)),
                (
                    "full_width",
                    models.ImageField(
                        height_field="full_width_image_height",
                        width_field="full_width_image_width",
                        upload_to="NOT_USED",
                        max_length=512,
                        blank=True,
                        null=True,
                        verbose_name="Image, full width of the site",
                    ),
                ),
                (
                    "half_width",
                    models.ImageField(
                        max_length=512,
                        upload_to="NOT_USED",
                        null=True,
                        verbose_name="Image, half the width of the site",
                        blank=True,
                    ),
                ),
                (
                    "third_width",
                    models.ImageField(
                        max_length=512,
                        upload_to="NOT_USED",
                        null=True,
                        verbose_name="Image, a third of the width of the site",
                        blank=True,
                    ),
                ),
                (
                    "quarter_width",
                    models.ImageField(
                        max_length=512,
                        upload_to="NOT_USED",
                        null=True,
                        verbose_name="Image, a quarter of the width of the site",
                        blank=True,
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        upload_to="NOT_USED",
                        max_length=512,
                        blank=True,
                        help_text="Always 120px by 120px, cropped to a square, centered on the image",
                        null=True,
                        verbose_name="Thumbnail version of the image",
                    ),
                ),
                (
                    "page_meta",
                    models.ForeignKey(
                        related_name="core_uploadedimage_uploads",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.PageMeta",
                        null=True,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        related_name="core_uploadedimage_site",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.Site",
                        null=True,
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="UploadedVideo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "containing_page_gid",
                    core.db.fields.UUIDField(max_length=64, null=True, blank=True),
                ),
                (
                    "gid",
                    core.db.fields.UUIDField(db_index=True, max_length=64, blank=True),
                ),
                ("asset_moved", models.BooleanField(default=False)),
                ("asset_move_failed", models.BooleanField(default=False)),
                (
                    "filedata",
                    models.FileField(
                        storage=django.core.files.storage.FileSystemStorage(
                            location="/home/vagrant/primarysite/static"
                        ),
                        upload_to=core.utils.file_storage.generate_path_original_filename,
                        max_length=512,
                        verbose_name="Source file provided",
                    ),
                ),
                (
                    "filedata_remote",
                    models.FileField(
                        upload_to=core.utils.file_storage.generate_path_original_filename,
                        max_length=512,
                        blank=True,
                        null=True,
                        verbose_name="Source file provided, remote",
                        db_index=True,
                    ),
                ),
                (
                    "pending_encoding",
                    models.BooleanField(
                        default=False,
                        help_text="If True, this asset has been submitted for encoding, but has not yet been completed",
                    ),
                ),
                (
                    "job_failed",
                    models.BooleanField(
                        default=False,
                        help_text="If True, the asset has been submitted for encoding, but the encoding job failed",
                    ),
                ),
                (
                    "last_encoding_job_id",
                    models.CharField(
                        help_text="This is the job ID reference for the last time the asset was submitted to the encoding service. If blank, it means the job has never been submitted. If non-blank, check the status of pending_encoding",
                        max_length=32,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "needs_reencoding",
                    models.BooleanField(
                        default=False,
                        help_text="Tick this if, for some reason, the converted clip needs re-converting from source'",
                        editable=False,
                    ),
                ),
                (
                    "duration_ms",
                    models.IntegerField(
                        help_text="Duration, in milliseconds, based on Zencoder's output",
                        null=True,
                        blank=True,
                    ),
                ),
                ("uploaded_on", models.DateTimeField(auto_now_add=True)),
                (
                    "output_still_cloud_uri",
                    models.CharField(
                        help_text="The address of the preview still in the Amazon S3 'bucket",
                        max_length=2000,
                        null=True,
                        blank=True,
                    ),
                ),
                ("output_still_height", models.IntegerField(null=True, blank=True)),
                ("output_still_width", models.IntegerField(null=True, blank=True)),
                (
                    "output_mp4_cloud_uri",
                    models.CharField(
                        help_text="The address of the converted MP4 file in the Amazon S3 'bucket'",
                        max_length=2000,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "output_mp4_cloud_size",
                    models.IntegerField(
                        help_text="Size, in bytes", null=True, blank=True
                    ),
                ),
                ("output_video_height", models.IntegerField(null=True, blank=True)),
                ("output_video_width", models.IntegerField(null=True, blank=True)),
                (
                    "page_meta",
                    models.ForeignKey(
                        related_name="core_uploadedvideo_uploads",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.PageMeta",
                        null=True,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        related_name="core_uploadedvideo_site",
                        on_delete=django.db.models.deletion.SET_NULL,
                        default=None,
                        blank=True,
                        to="core.Site",
                        null=True,
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("creator_id", models.IntegerField(null=True, blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("last_editor_id", models.IntegerField(null=True, blank=True)),
                ("ps_username", models.CharField(max_length=60, null=True)),
                (
                    "auth_user",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
                ("roles", models.ManyToManyField(to="core.SchoolUserRole", blank=True)),
                (
                    "school",
                    models.ForeignKey(
                        related_name="users",
                        blank=True,
                        to="core.School",
                        help_text="School this user is associated with, in whatever capacity",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "theme_editor_style",
                    models.ForeignKey(
                        blank=True,
                        to="core.ThemeEditorStyle",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="XMLSiteMapsRolloutSwitch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "site",
                    models.ForeignKey(
                        related_name="xml_sitemaps_rollout_switch",
                        to="core.Site",
                        help_text="The site that you want to ALLOW access to xml sitemaps messaging.",
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "XML Sitemap Rollout Switch",
                "verbose_name_plural": "XML Sitemap Rollout Switches",
            },
        ),
        migrations.AddField(
            model_name="theme",
            name="theme_type",
            field=models.ForeignKey(
                blank=True,
                to="core.ThemeType",
                help_text="Select which type of theme this is",
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="site",
            name="site_type",
            field=models.ForeignKey(
                related_name="sites",
                to="core.SiteType",
                help_text="Type of this site (primary/nursery)",
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="site",
            name="theme",
            field=models.ForeignKey(
                blank=True,
                to="core.Theme",
                help_text="The Theme that determines the look and feel of this site.\n        <br />If this is changed, you must re-save the theme in the theme\n         editor for automatic creation of Topics and Homepage slugs.",
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="site",
            name="twitter_account",
            field=models.ForeignKey(
                related_name="sites",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="twitter.Account",
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="pagerefpage", unique_together=set([("from_page", "to_page")]),
        ),
        migrations.AddField(
            model_name="pagemeta",
            name="site",
            field=models.ForeignKey(
                related_name="page_metas", to="core.Site", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="newsletteritem",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="newsitem",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="freesnippet",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="diaryentry",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="calendarcategory",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="baseslug",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="activitystreamproxy",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="activitystreamintrotext",
            name="site",
            field=models.ForeignKey(to="core.Site", on_delete=models.CASCADE),
        ),
        migrations.CreateModel(
            name="SiteProxy",
            fields=[],
            options={"proxy": True, "verbose_name_plural": "Sites' live status",},
            bases=("core.site",),
        ),
        migrations.AlterUniqueTogether(
            name="userprofile", unique_together=set([("ps_username", "school")]),
        ),
        migrations.AlterUniqueTogether(
            name="topic", unique_together=set([("slug", "site"), ("name", "site")]),
        ),
        migrations.AlterUniqueTogether(
            name="themetextfile", unique_together=set([("name", "theme")]),
        ),
        migrations.AlterUniqueTogether(
            name="themetemplate", unique_together=set([("name", "theme")]),
        ),
        migrations.AlterUniqueTogether(
            name="themeassetfile", unique_together=set([("name", "theme")]),
        ),
        migrations.AlterUniqueTogether(
            name="slideshow", unique_together=set([("site", "identifier")]),
        ),
        migrations.AlterUniqueTogether(
            name="schooluserrole", unique_together=set([("school", "role")]),
        ),
        migrations.AlterUniqueTogether(
            name="pagemeta", unique_together=set([("slug", "site")]),
        ),
        migrations.AlterUniqueTogether(
            name="freesnippet", unique_together=set([("site", "identifier")]),
        ),
        migrations.AlterUniqueTogether(
            name="eventcategories",
            unique_together=set([("calendar_category", "event")]),
        ),
        migrations.AlterUniqueTogether(
            name="calendarcategory", unique_together=set([("site", "colour")]),
        ),
        migrations.AlterUniqueTogether(
            name="baseslug", unique_together=set([("slug", "site")]),
        ),
        migrations.AlterUniqueTogether(
            name="activitystreamproxy",
            unique_together=set([("content_type", "object_id")]),
        ),
        migrations.AlterUniqueTogether(
            name="activitystreamintrotext", unique_together=set([("typename", "site")]),
        ),
    ]
