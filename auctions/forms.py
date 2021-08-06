from django.forms import ModelForm

from .models import *



class NewListingForm(ModelForm):

    class Meta:
        model = Listing
        fields = ['owner', 'title', 'description', 'starting_bid', 'image_url', 'category']


class SelectCategoryForm(forms.ModelForm):
    """ Offer choice of categories. """

    class Meta:
        model = Listing
        fields = ['category']


class NewBidForm(forms.ModelForm):
    """ form for bid """

    class Meta:
        model = Bid
        fields = ['bid']


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['contents']
