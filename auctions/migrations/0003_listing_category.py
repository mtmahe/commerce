# Generated by Django 3.2.4 on 2021-07-25 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('CL', 'Clothing'), ('EL', 'Electronics'), ('TY', 'Toys'), ('OT', 'Other')], default='CL', max_length=2),
        ),
    ]
