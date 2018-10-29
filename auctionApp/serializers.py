from rest_framework import serializers
from auctionApp.models import Auction
from django.contrib.auth.models import User
from accounts.models import UserProfile


class AuctionResourceGetSerializer(serializers.ModelSerializer):
	class Meta:
	    model = Auction
	    fields = ( 'title', 'description', 'minimum_price', 'previous_bid', 'bid_price',
	    	'timestamp', 'deadline', 'due')

