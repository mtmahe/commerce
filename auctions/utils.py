from .models import *


def query_listing(pk):
    """ Return listing given private key """

    listing = Listing.objects.get(pk=pk)

    return listing

def query_price(pk):
    """ returns the starting price or current highest bid price """

    listing = query_listing(pk)

    # Get current highest bid, first value is starting_bid
    if Bid.objects.filter(listing_id=pk).count() != 0:
        highest_bid = Bid.objects.filter(listing_id=pk).order_by('-id')[0]
        current_price = highest_bid.bid
    else:
        current_price = listing.starting_bid

    return current_price


def query_high_bidder(pk):
    """ Return high bidder or None """

    listing = query_listing(pk)

    if Bid.objects.filter(listing_id=pk).count() != 0:
        highest_bid = Bid.objects.filter(listing_id=pk).order_by('-id')[0]
        high_bidder = highest_bid.bidder
    else:
        high_bidder = None

    return high_bidder
