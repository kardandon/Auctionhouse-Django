import auctions
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import Auction_form, Bid_form, Comment_form

def index(request):
    ls = Auction_List.objects.filter(Active=True).all().values()
    for i in range(len(ls)):
        min_price = ls[i]["Starting_bid"]
        bids = Bid.objects.filter(Auction=ls[i]["id"]).order_by("-Money").values()
        if (len(bids)!= 0):
            min_price = bids[0]["Money"]
        ls[i]["Price"] = min_price
        ls[i]["lister"] = User.objects.filter(pk=ls[i]["lister_id"]).first().username
    return render(request, "auctions/index.html",{
        "auctions": ls,
        "message": None,
    })

@login_required(login_url="/login")
def new_auction(request):
    if request.method == "POST":
        form = Auction_form(request.POST)
        if form.is_valid():
            name = form.cleaned_data["Name"]
            description = form.cleaned_data["Description"]
            Category = form.cleaned_data["Category"]
            pic = form.cleaned_data["Pic_url"]
            starting_bid = float(form.cleaned_data["Starting_bid"])
            auc = Auction_List(Name=name,Description=description,Category=Category,lister=request.user,Pic_url=pic,Starting_bid=starting_bid, Active=True)
            auc.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new.html",{
            "form": form,
            "message": "Invalid form", 
        })
    else:
        return render(request, "auctions/new.html",{
            "form": Auction_form(),
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

def get_auction(request, id):
    auc = Auction_List.objects.filter(pk=id).first()
    watchlist = None
    is_owner = False
    if request.user.is_authenticated:
        is_owner = request.user == auc.lister
        watchlist = Watchlist.objects.filter(user_info=request.user).first()
    in_watchlist = False
    if watchlist != None:
        in_watchlist = auc in watchlist.auctions.all()
    if (request.method =="POST" and request.user.is_authenticated):
        if auc != None and request.POST["sneak"] == "comment":
            form = Comment_form(request.POST)
            print(form)
            Comment(auc=auc, comment=form.cleaned_data["comment"], commentor=request.user).save()
        elif auc != None and request.POST["sneak"] == "close":
            auc.Active = False
            auc.save()
        elif auc != None and request.POST["sneak"] == "bidding":
            minbid = auc.Starting_bid
            bid = Bid.objects.filter(Auction=auc, Bidder=request.user).all()
            money=float(request.POST["Money"])
            if (money > minbid):
                if (len(bid)== 0):
                    bid = Bid(Auction=auc, Bidder=request.user, Money=money)
                    bid.save()
                else:
                    maxbid = Bid.objects.filter(Auction=auc).all().order_by("-Money").first().Money
                    if maxbid < money:
                        bid.update_or_create(Auction=auc, Bidder=request.user, Money=money)
                    else:
                        return render(request, "auctions/index.html",{
                            "message": "Invalid money, please enter more",
                        })
            else:
                return render(request, "auctions/index.html",{
                    "message": "Invalid money, please enter more",
                })
        elif auc != None and request.POST["type"] == "add":
            if watchlist == None:
                watchlist= Watchlist(user_info=request.user)
                watchlist.save()
                watchlist.auctions.add(auc)
            else:
                watchlist.auctions.add(auc)
        elif auc != None and request.POST["type"] == "remove" and in_watchlist:
            watchlist.auctions.remove(auc)
        return HttpResponseRedirect(reverse("auction", kwargs={"id":id}))
    else:
        bids = Bid.objects.filter(Auction=auc).all()
        money = minbid = auc.Starting_bid
        user = "No one"
        comments = Comment.objects.filter(auc=auc).all()
        if(len(bids)!= 0):
            bid = bids.order_by("-Money").first()
            print(bid)
            money = bid.Money
            user = User.objects.filter(pk=bid.Bidder.id).first().username
            if user == request.user.username:
                user = "You"
        return render(request, "auctions/auction.html",{
            "auction": auc,
            "notFound": auc == None,
            "watched": in_watchlist,
            "num_bid": len(bids),
            "max_bidder": user,
            "money": money,
            "bid_form": Bid_form(),
            "is_owner": is_owner,
            "winner": user,
            "comments": comments,
            "comment_form": Comment_form(),
        })
@login_required(login_url="/login")
def watchlist(request):
    watchlist = Watchlist.objects.filter(user_info=request.user).first()
    if watchlist == None:
        watchlist= Watchlist(user_info=request.user)
        watchlist.save()
    aucs = watchlist.auctions.all().values()
    for i in range(len(aucs)):
        aucs[i]["lister"] = User.objects.filter(pk=aucs[i]["lister_id"]).first().username
        bid = Bid.objects.filter(Auction=aucs[i]["id"]).all().order_by("-Money").first()
        if bid != None:
            aucs[i]["money"] = bid.Money
            aucs[i]["maxbidder"] = User.objects.filter(pk=bid.Bidder.id).first().username
        else:
            aucs[i]["money"] = 0
            aucs[i]["maxbidder"] = "No one"
    return render(request, "auctions/watchlist.html",{
            "auctions": aucs,
        })

def category(request, cath):
    ls = Auction_List.objects.filter(Active=True, Category=cath).all().values()
    for i in range(len(ls)):
        min_price = ls[i]["Starting_bid"]
        bids = Bid.objects.filter(Auction=ls[i]["id"]).order_by("-Money").values()
        if (len(bids)!= 0):
            min_price = bids[0]["Money"]
        ls[i]["Price"] = min_price
        ls[i]["lister"] = User.objects.filter(pk=ls[i]["lister_id"]).first().username
    catname = Category.objects.filter(pk=cath).first().Category_name
    return render(request, "auctions/index.html",{
        "auctions": ls,
        "message": "Category: "+catname,
    })

def list_category(request):
    cats = Category.objects.all()
    return render(request, "auctions/cat.html",{
        "cats": cats,
    })
