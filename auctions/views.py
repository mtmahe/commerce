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

from .models import User, Listing, NewListingForm



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


def listing(request, listing_title):
    try:
        listing = Listing.objects.get(title=listing_title)
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    return render(request, "auctions/listing.html", {
        "title": listing_title,
        "listing": listing
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

    if request.method == "POST":
        listing = Listing.objects.get(pk=pk)

        if listing.owner != request.user:
            raise Http404("You are not the owner of that listing.")
        listing.active = False
        listing.save()

        return render(request, "auctions/listing.html", {
            "pk": pk
        })


    return render(request, "auctions/close.html", {
        "pk": pk
    })
