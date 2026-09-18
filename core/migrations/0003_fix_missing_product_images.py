from django.db import migrations


def fix_missing_product_images(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    Product.objects.filter(image_url="Media/download_8.jpg").update(
        image_url="Media/1781794098_99eb11a52b6f5c486674.webp"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_rename_category_choices_category_and_more"),
    ]

    operations = [
        migrations.RunPython(fix_missing_product_images, migrations.RunPython.noop),
    ]