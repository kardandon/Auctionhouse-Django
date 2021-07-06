from django.forms.widgets import Textarea
from auctions.models import Category
from django import forms
from .models import Auction_List, Comment

class Auction_form(forms.ModelForm):
    class Meta:
        model = Auction_List
        fields = ["Name", "Description", "Category", "Pic_url","Starting_bid"]
        widgets = {
            "Desription": forms.Textarea(),
        }
class Bid_form(forms.Form):
    Money = forms.FloatField()

class Comment_form(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]