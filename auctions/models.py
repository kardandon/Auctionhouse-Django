from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import CharField


class User(AbstractUser):
    pass

class Category(models.Model):
    Category_name = CharField(max_length=64)

    def __str__(self):
        return f"{self.Category_name}"

class Auction_List(models.Model):
    Active = models.BooleanField()
    Starting_bid = models.FloatField()
    Name = models.CharField(max_length=64)
    Description = models.CharField(max_length=64)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listed_items")
    Category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listed_items")
    Pic_url = models.CharField(max_length=128)
    def __str__(self):
        return f"{self.Name} from {self.Category} listed by {self.lister}"

class Watchlist(models.Model):
    auctions = models.ManyToManyField(Auction_List, blank=True, related_name="watchlisted")
    user_info = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_watchlist")
    def __str__(self):
        return f"{self.user_info}: {self.auctions}"

class Bid(models.Model):
    Bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    Auction = models.ForeignKey(Auction_List, on_delete=models.CASCADE, related_name="bids")
    Money = models.FloatField()
    def __str__(self):
        return f"{self.Bidder} to {self.Auction}: {self.Money} dollars"

class Comment(models.Model):
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auc = models.ForeignKey(Auction_List, on_delete=models.CASCADE, related_name="auc_comment")
    comment = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.commentor.username}: {self.comment}"