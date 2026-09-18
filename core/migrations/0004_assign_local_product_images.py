from django.db import migrations


IMAGE_BY_PRODUCT = {
    "Aurora Pearl Set": "Media/download_3_1.jpg",
    "Velvet Bloom Ring": "Media/1781794098_99eb11a52b6f5c486674.webp",
    "Royal Gold Necklace": "Media/-473Wx593H-702463602-gold-MODEL.avif",
    "Sunlit Gold Bangle": "Media/-473Wx593H-702463602-gold-MODEL.avif",
    "Starlight Diamond Earrings": "Media/AMS-104-3666.webp",
    "Celeste Diamond Ring": "Media/1781794098_99eb11a52b6f5c486674.webp",
    "Eternal Bridal Set": "Media/AMS-104-3666.webp",
    "Pearl Romance Bridal Necklace": "Media/download_3_1.jpg",
    "Moonlit Collection Pendant": "Media/download_6.jpg",
    "Gardenia Collection Cuff": "Media/-473Wx593H-702463602-gold-MODEL.avif",
    "Weekend Luxe Charm": "Media/download_6.jpg",
    "Lite Gold Duo": "Media/download_3_1.jpg",
}


def assign_local_product_images(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    for name, image_path in IMAGE_BY_PRODUCT.items():
        Product.objects.filter(name=name).update(image_url=image_path)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_fix_missing_product_images"),
    ]

    operations = [
        migrations.RunPython(assign_local_product_images, migrations.RunPython.noop),
    ]