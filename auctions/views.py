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
from django import forms
from django.forms import ModelForm, Textarea

from django.views.generic import CreateView, ListView, DetailView, UpdateView

from .models import (
    User,
    Listing,
    NewListingForm,
    Bid,
    NewBidForm,
    Comment,
    NewCommentForm
)



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


class ListingListView(ListView):
    """ list our active posts """

    model = Listing
    template_name = 'auctions/index.html'
    context_object_name = 'listings'


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


@login_required()
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

    else:
        newBidForm = NewBidForm()
        newCommentForm = NewCommentForm()

    # Get current highest bid, first value is starting_bid
    try:
        current_price = Bid.objects.filter(listing_id=pk).order_by('-id')[0].bid
    except:
        current_price = listing.starting_bid

    # Number of bids
    bid_count = Bid.objects.filter(listing_id=pk).count()
    # Comments
    comments = Comment.objects.filter(listing_id=pk)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "pk": pk,
        "newBidForm": newBidForm,
        "current_price": current_price,
        "bid_count": bid_count,
        "comments": comments,
        "newCommentForm": newCommentForm,
    })


class ListingDetailView(LoginRequiredMixin, DetailView):
    """ list our active posts """

    model = Listing
    template_name = 'auctions/listing.html'
    context_object_name = 'listing'


class ListingCreateView(LoginRequiredMixin, CreateView):
    """ Create a new listing. """

    model = Listing
    template_name = 'auctions/create.html'
    fields = ['title', 'description', 'starting_bid', 'image_url', 'category']

    #override form valid so if will let us set owner before validation
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """ Allow owner to close the auction, setting highest bidder as winner. """

    def test_func(self):
        listing = self.get_object()
        if self.request.user == listing.owner:
            return True
        return False


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
