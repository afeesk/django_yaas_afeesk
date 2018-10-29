from django import forms
from .models import Auction

class AuctionForm(forms.ModelForm):
	class Meta:
		model = Auction
		fields = ['title','description','minimum_price','deadline']

	def save(self, commit = True):
		auction = super(AuctionForm, self).save(commit = False)
		if commit:
			auction.save()
		return auction


class AuctionUpdateForm(forms.ModelForm):
	class Meta:
		model = Auction
		fields = ['description']
		

	def save(self, commit = True):
		auction = super(AuctionUpdateForm, self).save(commit = False)
		if commit:
			auction.save()
		return auction

class ConfirmPostAuctionForm(forms.ModelForm):

	CHOICES = (('Yes', 'YES' ), ('No', 'NO'))
	option = forms.ChoiceField(choices=CHOICES, required = False)
	title = forms.CharField(widget=forms.HiddenInput())
	description = forms.CharField(widget=forms.HiddenInput())
	minimum_price = forms.CharField(widget=forms.HiddenInput())
	deadline = forms.CharField(widget=forms.HiddenInput())


	class Meta:
		model = Auction
		fields = ['description']

class ConfirmAuctionUpdateForm(forms.ModelForm):

	CHOICES = (('Yes', 'YES' ), ('No', 'NO'))
	option = forms.ChoiceField(choices=CHOICES, required = False)
	description = forms.CharField(widget=forms.HiddenInput())

	class Meta:
		model = Auction
		fields = ['description']



		
class AuctionBidForm(forms.ModelForm):
	class Meta:
		model = Auction
		#Mandate bid increament to 0.01 and only 2 decimal places when bidding
		fields = ['bid_price']
		#fields = ['description']

	def save(self, commit = True):
		auction = super(AuctionBidForm, self).save(commit = False)
		if commit:
			auction.save()
		return auction
