import random
import django.dispatch 
import hashlib
from django.conf import settings
#from .models import AuctionCreatedEmail
from .models import Auction, AuctionEmail, Bid, BidEmail
import datetime

from django.db.models.signals import post_save
from django.utils.timezone import utc
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import send_mail
from auction.process_bidders import get_bidder_email
from django.contrib.auth import get_user_model

User = settings.AUTH_USER_MODEL
# try:
#     from django.contrib.auth import get_user_model

# except ImportError:
#     from django.contrib.auth.models import User 

#User = get_user_model()

# def auction_ban_send_email(sender, instance, created, *args, **kwargs):
# 		auction = instance
# 		if created:
# 			email_confirmed, email_is_created = AuctionEmail.objects.get_or_create(auction = auction)
# 			auction_is_banned, auction_is_created = AuctionEmail.objects.get_or_create(auction = auction)
# 			if auction_is_created:
# 				auction_is_banned.save()
# 				auction_is_banned.email_user()


#post_save.connect(auction_ban_send_email, sender= Auction)

def auction_ban_or_create_send_email(sender, instance, created, *args, **kwargs):
	auction = instance
	seller_email = auction.seller.email
	all_bids = Bid.objects.all().filter(auction=auction)
	seller, bidders_email_list =  get_bidder_email(all_bids, seller_email)
	auction_get, auction_is_created = AuctionEmail.objects.get_or_create(auction=auction)
	if created:
			auction_get.auction_created_email()
	else:
		if auction_get.auction_is_banned() == True:
			auction_get.banned_auction_email(seller, bidders_email_list)

		if auction_get.auction_is_adjucated() == True:
			auction_get.winning_auction_email(seller, bidders_email_list)

post_save.connect(auction_ban_or_create_send_email, sender= Auction)


def bid_create_send_email(sender, instance, created, *args, **kwargs):
	bid = instance
	seller_email = bid.auction.seller.email
	bid_get, bid_is_created = BidEmail.objects.get_or_create(bid=bid)
	all_bids = Bid.objects.all().filter(auction__slug=bid.auction.slug)
	winner, bidders_email_list =  get_bidder_email(all_bids, seller_email)
	#print "bid_get is", 
	if created:
				bid_get.bid_created_email(bidders_email_list)		

post_save.connect(bid_create_send_email, sender= Bid)
