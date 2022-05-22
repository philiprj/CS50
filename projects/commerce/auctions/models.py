from mimetypes import init
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"


class Listing(models.Model):
    # Listing details
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=612)
    picture = models.ImageField()
    category = models.ForeignKey(Category)
    # Bid details
    initial_bid = models.DecimalField(max_digits=2)
    current_bid = models.DecimalField(max_digits=2)
    created_date = models.DateTimeField(auto_now_add=True)
    # User details
    creator = models.ForeignKey(User)
    watchers = models.ManyToManyField(User)
    buyer = models.ForeignKey(User)

    def __str__(self):
        return f"{self.name} -- {self.current_bid}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing)
    bid_price = models.DecimalField(max_digits=2)
    bidder = models.ForeignKey(User)
    bid_time = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    commenter = models.ForeignKey(User)
    comment_time = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=256)
