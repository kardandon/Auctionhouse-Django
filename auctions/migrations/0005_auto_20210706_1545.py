# Generated by Django 3.2.5 on 2021-07-06 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20210706_1513'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='money',
            new_name='Money',
        ),
        migrations.AddField(
            model_name='bid',
            name='Auction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.auction_list'),
            preserve_default=False,
        ),
    ]
