# Generated by Django 3.1.7 on 2023-02-17 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demoApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cameraset',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='cameraset',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
    ]
