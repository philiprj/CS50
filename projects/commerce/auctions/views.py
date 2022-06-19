from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from django import forms
from django.forms import ModelForm, modelformset_factory
from django.contrib.auth.decorators import login_required


def index(request):
    # return render(request, "auctions/index.html")
    return activeListings(request)


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class newListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["name", "description", "initial_bid", "category"]


class newPictureForm(ModelForm):
    class Meta:
        model = Picture
        fields = ["picture", "alt_text"]


class newBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["bid_price"]


class newCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Leave your comment here",
                }
            )
        }


@login_required
def newListing(request):
    PictureFormSet = modelformset_factory(Picture, form=newPictureForm, extra=4)
    if request.method == "POST":
        form = newListingForm(request.POST, request.FILES)
        imagesForm = PictureFormSet(
            request.POST, request.FILES, queryset=Picture.objects.none()
        )
        if form.is_valid() and imagesForm.is_valid():
            newListing = form.save(commit=False)
            newListing.creator = request.user
            newListing.save()

            for form in imagesForm.cleaned_data:
                if form:
                    picture = form["picture"]
                    text = form["alt_text"]
                    newPicture = Picture(
                        listing=newListing, picture=picture, alt_text=text
                    )
                    newPicture.save()

            return render(
                request,
                "auctions/newListing.html",
                {
                    "form": newListingForm(),
                    "imageForm": PictureFormSet(queryset=Picture.objects.none()),
                    "success": True,
                },
            )
        else:
            return render(
                request,
                "auctions/newListing.html",
                {
                    "form": newListingForm(),
                    "imageForm": PictureFormSet(queryset=Picture.objects.none()),
                },
            )

    else:
        return render(
            request,
            "auctions/newListing.html",
            {
                "form": newListingForm(),
                "imageForm": PictureFormSet(queryset=Picture.objects.none()),
            },
        )


def activeListings(request):
    category_id = request.GET.get("category", None)
    if category_id is None:
        listings = Listing.objects.filter(active=True)
    else:
        listings = Listing.objects.filter(active=True, category=category_id)
    categories = Category.objects.all()
    for listing in listings:
        listing.mainPicture = listing.get_pictures.first()
        if request.user in listing.watchers.all():
            listing.is_watched = True
        else:
            listing.is_watched = False
    return render(
        request,
        "auctions/index.html",
        {
            "listings": listings,
            "categories": categories,
            "page_title": "Active Listings",
        },
    )


@login_required
def watchlist(request):
    listings = request.user.watched.all()
    categories = Category.objects.all()
    for listing in listings:
        listing.mainPicture = listing.get_pictures.first()
        if request.user in listing.watchers.all():
            listing.is_watched = True
        else:
            listing.is_watched = False
    return render(
        request,
        "auctions/index.html",
        {"listings": listings, "page_title": "My watchlist", "categories": categories},
    )


@login_required
def change_watchlist(request, listing_id, reverse_method):
    listing_object = Listing.objects.get(id=listing_id)
    if request.user in listing_object.watchers.all():
        listing_object.watchers.remove(request.user)
    else:
        listing_object.watchers.add(request.user)

    if reverse_method == "listing":
        return listing(request, listing_id)
    else:
        return HttpResponseRedirect(reverse(reverse_method))


def listing(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    listing = Listing.objects.get(id=listing_id)
    if request.user in listing.watchers.all():
        listing.is_watched = True
    else:
        listing.is_watched = False
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "listing_pictures": listing.get_pictures.all(),
            "form": newBidForm(),
            "comments": listing.comments.all(),
            "comment_form": newCommentForm(),
        },
    )


@login_required
def take_bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bid_price = float(request.POST["bid_price"])
    if is_valid(bid_price, listing):
        listing.current_bid = bid_price
        form = newBidForm(request.POST)
        newBid = form.save(commit=False)
        newBid.listing = listing
        newBid.user = request.user
        newBid.save()
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listing,
                "listing_pictures": listing.get_pictures.all(),
                "form": newBidForm(),
                "error_min_value": True,
            },
        )


def is_valid(bid_price, listing):
    if bid_price >= listing.initial_bid and (
        listing.current_bid is None or bid_price > listing.current_bid
    ):
        return True
    else:
        return False


def close_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.user == listing.creator:
        listing.active = False
        listing.buyer = Bid.objects.filter(auction=listing).last().user
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        listing.watchers.add(request.user)
    return HttpResponseRedirect(reverse("watchlist"))


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    form = newCommentForm(request.POST)
    newComment = form.save(commit=False)
    newComment.user = request.user
    newComment.listing = listing
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
