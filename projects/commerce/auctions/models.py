from distutils.command.upload import upload
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
    description = models.CharField(max_length=612, null=True)
    picture = models.ImageField(upload_to="images/")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="similar"
    )
    active = models.BooleanField(default=True)
    # Bid details
    initial_bid = models.DecimalField(max_digits=2)
    current_bid = models.DecimalField(max_digits=2, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    # User details
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_listings"
    )
    watchers = models.ManyToManyField(User, blank=True, related_name="watched")
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.name} -- {self.current_bid}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_time = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )
    comment_time = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=256)
