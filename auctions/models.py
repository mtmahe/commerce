from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.urls import reverse



class User(AbstractUser):
    pass


class Listing(models.Model):
    CLOTHING = 'CL'
    ELECTRONICS = 'EL'
    TOYS = 'TY'
    OTHER = 'OT'
    category_choices =[
        (CLOTHING, 'Clothing'),
        (ELECTRONICS, 'Electronics'),
        (TOYS, 'Toys'),
        (OTHER, 'Other')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="proprietor")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=2000)
    starting_bid = models.DecimalField(max_digits=9, decimal_places=2)
    image_url = models.URLField(max_length=64)
    category = models.CharField(max_length=2, choices = category_choices, default=CLOTHING)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Owner: {self.owner.username} First: {self.owner.first_name} Title: {self.title}"

    def get_absolute_url(self):
        return reverse('listing', kwargs={'pk': self.pk})


class Bid(models.Model):
    """ Keep track of all bids. """

    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="the_bid")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="the_bidder")
    bid = models.DecimalField(max_digits=9, decimal_places=2) #make sure higher than previous bid

    def __str__(self):
        return f"Listing id: {self.listing_id.id} Bidder: {self.bidder.username} Bid: {self.bid}"


class Comment(models.Model):
    """ A table for comments on each listing page. """

    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_listing")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_commenter")
    contents = models.TextField(max_length=900, verbose_name="", help_text="")


class Watchlist(models.Model):
    """ A table for watch list. """

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="the_watched_listing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="the_watcher")

    def __str__(self):
        return f"{self.user.username} watching {self.listing.id}"

    def get_absolute_url(self):
        return reverse('watchlist-view', kwargs={'pk': self.pk})
