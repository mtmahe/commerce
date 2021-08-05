from django.urls import path
from .views import ListingCreateView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:pk>/", views.listing, name="listing"),
    path("listing/create/", ListingCreateView.as_view(), name="listing-create"),
    path("listing/<int:pk>/close/", views.close_auction_view, name="listing-close"),
    path("watchlist/", views.watchlist, name="watchlist-view"),
    path("categories/", views.categories, name="categories-view"),
]
