# Generated by Django 3.0.8 on 2020-08-13 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_auto_20200813_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='active_list',
            name='won_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='won', to='auctions.bids'),
        ),
    ]
