# Generated by Django 4.0.4 on 2022-06-19 11:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=612, null=True)),
                ('picture', models.ImageField(upload_to='images/')),
                ('active', models.BooleanField(default=True)),
                ('initial_bid', models.FloatField()),
                ('current_bid', models.FloatField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similar', to='auctions.category')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_listings', to=settings.AUTH_USER_MODEL)),
                ('watchers', models.ManyToManyField(blank=True, related_name='watched', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_time', models.DateTimeField(auto_now=True)),
                ('comment', models.CharField(max_length=256)),
                ('commenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='auctions.listing')),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_price', models.FloatField()),
                ('bid_time', models.DateTimeField(auto_now=True)),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.listing')),
            ],
        ),
    ]
