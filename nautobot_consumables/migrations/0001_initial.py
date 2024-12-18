# Generated by Django 3.2.25 on 2024-07-15 16:49
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator
from django.db import migrations, models
from django.db.models import deletion
from nautobot.core.models.fields import NaturalOrderingField
from nautobot.core.models.ordering import naturalize
from nautobot.extras.models.mixins import DynamicGroupMixin, NotesMixin
from taggit.managers import TaggableManager


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("extras", "0058_jobresult_add_time_status_idxs"),
        ("dcim", "0023_interface_redundancy_group_data_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="Consumable",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=DjangoJSONEncoder,
                    ),
                ),
                ("data", models.JSONField(blank=True, null=True)),
                ("schema", models.JSONField(blank=True, null=True)),
                ("name", models.CharField(db_index=True, max_length=100, unique=True)),
                (
                    "_name",
                    NaturalOrderingField(
                        "name",
                        blank=True,
                        db_index=True,
                        max_length=255,
                        naturalize_function=naturalize,
                    ),
                ),
                ("product_id", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "Consumable",
                "verbose_name_plural": "Consumables",
                "ordering": ["consumable_type", "_name"],
            },
            bases=(models.Model, DynamicGroupMixin, NotesMixin),
        ),
        migrations.CreateModel(
            name="ConsumableType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=DjangoJSONEncoder,
                    ),
                ),
                ("data", models.JSONField(blank=True, null=True)),
                ("schema", models.JSONField(blank=True, null=True)),
                ("name", models.CharField(db_index=True, max_length=100, unique=True)),
                (
                    "_name",
                    NaturalOrderingField(
                        "name",
                        blank=True,
                        db_index=True,
                        max_length=255,
                        naturalize_function=naturalize,
                    ),
                ),
                ("tags", TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Consumable Type",
                "verbose_name_plural": "Consumable Types",
            },
            bases=(models.Model, DynamicGroupMixin, NotesMixin),
        ),
        migrations.CreateModel(
            name="ConsumablePool",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=100)),
                (
                    "_name",
                    NaturalOrderingField(
                        "name",
                        blank=True,
                        db_index=True,
                        max_length=255,
                        naturalize_function=naturalize,
                    ),
                ),
                ("quantity", models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])),
                (
                    "consumable",
                    models.ForeignKey(
                        on_delete=deletion.PROTECT,
                        related_name="pools",
                        to="nautobot_consumables.consumable",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=deletion.PROTECT,
                        related_name="consumable_pools",
                        to="dcim.location",
                    ),
                ),
                ("tags", TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Consumable Pool",
                "verbose_name_plural": "Consumable Pools",
                "ordering": ["consumable", "location", "name"],
                "unique_together": {("consumable", "location", "name")},
            },
            bases=(models.Model, DynamicGroupMixin, NotesMixin),
        ),
        migrations.AddField(
            model_name="consumable",
            name="consumable_type",
            field=models.ForeignKey(
                on_delete=deletion.PROTECT,
                to="nautobot_consumables.consumabletype",
            ),
        ),
        migrations.AddField(
            model_name="consumable",
            name="manufacturer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=deletion.PROTECT,
                to="dcim.manufacturer",
            ),
        ),
        migrations.AddField(
            model_name="consumable",
            name="tags",
            field=TaggableManager(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AlterUniqueTogether(
            name="consumable",
            unique_together={("manufacturer", "consumable_type", "product_id")},
        ),
        migrations.CreateModel(
            name="CheckedOutConsumable",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=DjangoJSONEncoder,
                    ),
                ),
                ("quantity", models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])),
                (
                    "consumable_pool",
                    models.ForeignKey(
                        on_delete=deletion.PROTECT,
                        related_name="checked_out",
                        to="nautobot_consumables.consumablepool",
                    ),
                ),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=deletion.PROTECT,
                        related_name="consumables",
                        to="dcim.device",
                    ),
                ),
                ("tags", TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "Checked Out Consumable",
                "verbose_name_plural": "Checked Out Consumables",
                "ordering": ["consumable_pool", "device"],
                "unique_together": {("device", "consumable_pool")},
            },
            bases=(models.Model, DynamicGroupMixin, NotesMixin),
        ),
    ]
