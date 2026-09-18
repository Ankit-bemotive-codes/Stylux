from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_address_options_alter_address_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
