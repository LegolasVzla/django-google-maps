# Generated by Django 3.0.7 on 2020-08-13 18:59

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20190808_0314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spots',
            name='geom',
            field=django.contrib.gis.db.models.fields.GeometryField(null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='spots',
            name='lat',
            field=models.DecimalField(decimal_places=16, max_digits=22, null=True),
        ),
        migrations.AlterField(
            model_name='spots',
            name='lng',
            field=models.DecimalField(decimal_places=16, max_digits=22, null=True),
        ),
        migrations.AlterField(
            model_name='spots',
            name='position',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]
