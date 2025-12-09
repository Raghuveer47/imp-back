# Generated manually for Cloudinary integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_employeelocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='face_image_cloudinary_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='face_image_cloudinary_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='image_cloudinary_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='image_cloudinary_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ] 