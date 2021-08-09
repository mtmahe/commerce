from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest
)
from django.shortcuts import render
from django.urls import reverse#
from django import forms, template
from django.forms import ModelForm, Textarea

from django.views.generic import CreateView, ListView, DetailView, UpdateView

from .models import *
from .forms import *
from .utils import *



def index(request):
    """ Displays all current active listings with a summary. """

    listings = []
    all_listings = Listing.objects.filter(active=True)
    for listing in all_listings:
        pk = listing.pk
        price = query_price(pk)
        listing.price = price

    return render(request, "auctions/index.html", {
        "listings": all_listings,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def listing(request, pk):
    """ Show the listing. If owned, can close. If open, can bid or comment.

    If a first bid is received must be >= starting price. If there has already
    been a bid, the new bid must be greater. """

    try:
        listing = Listing.objects.get(pk=pk)
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")


    if request.method == 'POST':

        # Are they submitting a bid?
        if 'submit-bid' in request.POST:
            newBidForm = NewBidForm(request.POST)
            newBidForm.instance.bidder = request.user
            newBidForm.instance.listing_id = listing
            newCommentForm = NewCommentForm()
            if newBidForm.is_valid():
                new_bid = newBidForm.cleaned_data['bid']

                # Check if there has already been a bid then use correct rule.
                if Bid.objects.filter(listing_id=pk).count() > 0:
                    previous_bid = Bid.objects.filter(listing_id=pk).order_by('-id')[0].bid
                    if new_bid > previous_bid:
                        newBidForm.save()
                        messages.success(request, 'Bid saved successfully.')
                    else:
                        messages.error(request, 'Error: New bid must be greater than previous bid.')
                else:
                    starting_price = listing.starting_bid
                    if new_bid >= starting_price:
                        newBidForm.save()
                        messages.success(request, 'Bid saved successfully.')
                    else:
                        messages.error(request, 'Error: First bid must be greater than or equal to starting price.')

        # Or are they submitting a comment?
        elif 'submit-comment' in request.POST:
            newCommentForm = NewCommentForm(request.POST)
            newCommentForm.instance.listing_id = listing
            newCommentForm.instance.commenter = request.user
            newBidForm = NewBidForm()
            if newCommentForm.is_valid():
                newCommentForm.save()
                messages.success(request, 'Comment saved successfully.')
            else:
                messages.error(request, 'Error: Please only enter text and punctuation in comment.')

        # Or are they toggling watchlist?
        elif 'watch-button' in request.POST:
            if not Watchlist.objects.filter(user=request.user, listing=listing):
                watchlist = Watchlist()
                watchlist.listing = listing
                watchlist.user = request.user
                watchlist.save()
                messages.success(request, 'Saved to Watchlist')
            else:
                print('unsaving')
                Watchlist.objects.filter(user=request.user).delete()
                messages.success(request, 'Removed from Watchlist')
            newBidForm = NewBidForm()
            newCommentForm = NewCommentForm()

    # It's GET
    else:
        newBidForm = NewBidForm()
        newCommentForm = NewCommentForm()

    current_price = query_price(pk)
    high_bidder = query_high_bidder(pk)
    bid_count = Bid.objects.filter(listing_id=pk).count()
    comments = Comment.objects.filter(listing_id=pk)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "pk": pk,
        "newBidForm": newBidForm,
        "current_price": current_price,
        "bid_count": bid_count,
        "comments": comments,
        "newCommentForm": newCommentForm,
        "high_bidder": high_bidder
    })


class ListingCreateView(LoginRequiredMixin, CreateView):
    """ Create a new listing. """

    model = Listing
    template_name = 'auctions/create.html'
    fields = ['title', 'description', 'starting_bid', 'image_url', 'category']

    #override form valid so if will let us set owner before validation
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


def close_auction_view(request, pk):
    """ Option to close the listing setting active to false."""

    print("hello")

    if request.method == "POST":
        listing = Listing.objects.get(pk=pk)

        if listing.owner != request.user:
            raise Http404("You are not the owner of that listing.")

        print("got here")
        listing.active = False
        listing.save()

        url = reverse('listing', kwargs={'pk': pk})
        return HttpResponseRedirect(url)

    return render(request, "auctions/close.html", {
        "pk": pk
    })


@login_required
def watchlist(request):
    """ Show summary page for items being watched """

    return render(request, "auctions/watchlist.html", {
        "watches": Watchlist.objects.all()
    })


def categories(request):
    """ Give a view of active listings by category """

    if request.method == "POST":
        selectCategoryForm = SelectCategoryForm(request.POST)
        if selectCategoryForm.is_valid():
            selected_category = selectCategoryForm.cleaned_data['category']

    else: # It must be GET
        selected_category = 'CL'
        selectCategoryForm = SelectCategoryForm()

    return render(request, "auctions/categories.html", {
        "listings": Listing.objects.filter(category=selected_category),
        "selectCategoryForm": selectCategoryForm,
    })
