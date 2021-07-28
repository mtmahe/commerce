# Generated by Django 3.2.4 on 2021-07-22 19:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=2000)),
                ('starting_bid', models.DecimalField(decimal_places=2, max_digits=9)),
                ('image_url', models.URLField(max_length=64)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proprietor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]