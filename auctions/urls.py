from auctions.models import Watchlist
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_auction, name= "new"),
    path("auction/<str:id>", views.get_auction, name="auction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<str:cath>", views.category, name="category"),
    path("category/", views.list_category, name="list_category")
]
