# Generated by Django 5.0.1 on 2024-01-06 22:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_melivendor"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="meliitem",
            options={"ordering": ["-price"]},
        ),
        migrations.AlterModelOptions(
            name="melivendor",
            options={"ordering": ["-total_items"]},
        ),
    ]