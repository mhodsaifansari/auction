# Generated by Django 3.0.8 on 2020-08-12 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_active_list_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='placed_on',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.active_list'),
        ),
    ]
