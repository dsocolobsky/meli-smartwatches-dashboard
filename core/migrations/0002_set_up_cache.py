# This migration sets up default values for the cache.

from django.db import migrations


def set_up_cache_data(apps, schema_editor):
    CacheData = apps.get_model("core", "CacheData")
    CacheData.objects.create(
        most_expensive_cache_minutes=1,
        vendor_data_cache_minutes=1,
        most_expensive_last_update="2024-01-01 00:01",
        vendor_data_last_update="2024-01-01 00:01",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_up_cache_data),
    ]
