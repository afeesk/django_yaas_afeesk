from django.db import models
from django.conf import settings
from pytz import timezone
import pytz
from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.mail import send_mass_mail, send_mail, send_mass_mail
from django.template.loader import render_to_string
#from django.db.models.signals import post_save
from django.utils.timezone import utc
from django.utils import timezone
from auction.process_bidders import get_bidder_email

def get_deadline():
    return datetime.utcnow().replace(tzinfo=pytz.utc)+timedelta(seconds = 259200)


class Auction(models.Model):
	seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank= True, on_delete=models.PROTECT)
	title = models.CharField(max_length = 120, null = False, blank = False)
	description = models.TextField(max_length = 200, null = False, blank = False)
	minimum_price = models.DecimalField(decimal_places=2, max_digits=100, default=0.01)
	d_version = models.IntegerField(default=0)
	bid_version = models.IntegerField(default=0)
	previous_bid = models.DecimalField(decimal_places=2, max_digits=100, default=0.01)
	bid_price = models.DecimalField(decimal_places=2, max_digits=100, default=0.01)
	timestamp = models.DateTimeField(auto_now_add =True, auto_now =False)
	deadline = models.DateTimeField(default=get_deadline)
	active = models.BooleanField(default =True)
	banned = models.BooleanField(default =False)
	due = models.BooleanField(default =False)
	adjucated = models.BooleanField(default =False)
	slug = models.SlugField(unique=True)
	current_winning_bidder = models.CharField(max_length = 120, null = True, blank = True)


	def __str__(self):
			return self.title

	class Meta:
			#unique together checks if both title and slug are already unique, will tell me if i try add another same title with same slug
			unique_together = ('title','slug')

	def get_absolute_url(self):
		return reverse("single_product", kwargs={"slug":self.slug})

	def get_active(self):
		return self.active


	def set_expired(self, *args, **kwargs):
		#current_date = timezone.now() #datetime.datetime.utcnow().replace(tzinfo=utc)
		date_now = datetime.utcnow().replace(tzinfo=pytz.utc)
		deadline = self.deadline
		if date_now > deadline:
			self.due = True
			self.active = False
			super(Auction, self).save(*args, **kwargs)
		else:
			pass

	def set_adjucated(self, *args, **kwargs):
			self.due = True
			self.adjucated = True
			super(Auction, self).save(*args, **kwargs)



class BidManager(models.Manager):
    def bids(self, auction):
    	return super(BidManager, self).get_queryset().filter(auction = auction)

class Bid(models.Model):
	auction = models.ForeignKey(Auction, null = True, on_delete=models.PROTECT)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bidder', null=False, blank= False, on_delete=models.PROTECT)
	bid_amount = models.DecimalField(decimal_places=2, max_digits=100, default=0.01)
	objects = models.Manager()
	actual_bids = BidManager()
	#bids 

	def __str__(self):
			return self.auction.title


	def bid_created(self, bids):
		winner_amount = 0
		winner = ""
		bidder_email_list = []
		for items in bids:
			if items.user.email != auction.seller.email:
				bidder_email_list.append(items.user.email)
			if items.bid_amount>winner_amount:
				winner_amount = items.bid_amount
				winner = items.user
				winner_email = items.user.email
		deduped_bidders_email =  list(set(bidder_email_list))
		bidder_email_str = ','.join(deduped_bidders_email)
		return (winner, bidder_email_str)	


class AuctionEmail(models.Model):
	auction = models.ForeignKey("Auction", on_delete=models.PROTECT)

	def __str__(self):
		return self.auction

	def auction_is_banned(self):
		return self.auction.banned

	def auction_is_adjucated(self):
		return self.auction.adjucated

	def auction_created_email(self):
		context = {

				 	"user": self.auction.seller,
				 	"slug": self.auction.slug,
				 	"web_url": settings.SITE_URL,
				 }
		message = render_to_string("auction_created.txt", context)
		subject = "New Auction Created"
		send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.auction.seller.email])
	
	#def banned_auction_email(self, winner, bidder_emails):
	def banned_auction_email(self, winner, bidder_emails):
		seller_email = self.auction.seller.email
		#winner_email = winner.email
		context = {

				 	"seller": self.auction.seller,
				 	"slug": self.auction.slug,
				 	"title": self.auction.title,
				 }
		seller_message = render_to_string("seller_banned_email.txt", context)
		bidder_message = render_to_string("bidder_banned_email.txt", context)
		seller_subject = "Your item is banned"
		bidder_subject = "An item you bid on has been banned"
		datatuple = (
			(seller_subject, seller_message, settings.DEFAULT_FROM_EMAIL, [seller_email]),
			(bidder_subject, bidder_message, settings.DEFAULT_FROM_EMAIL, [bidder_emails]),
			#(bidder_subject, bidder_message, settings.DEFAULT_FROM_EMAIL, [winner_email]),
			)
		send_mass_mail(datatuple)

	def winning_auction_email(self, winner, bidder_emails):
		seller_email = self.auction.seller.email
		winner_email = winner.email
		print(winner_email)
		print(bidder_emails)
		context = {

				 	"seller": self.auction.seller,
				 	"winner":winner,
				 	"title": self.auction.title,
				 }
		seller_message = render_to_string("seller_winning_email.txt", context)
		bidder_message = render_to_string("bidder_winning_email.txt", context)
		winner_message = render_to_string("bidder_winner_email.txt", context)
		seller_subject = "One of your item has a winning bidder"
		bidder_subject = "An item you bid on has been won"
		winner_subject = "Your bid has won. Congratulations! "
		datatuple = (
			(seller_subject, seller_message, settings.DEFAULT_FROM_EMAIL, [seller_email]),
			(bidder_subject, bidder_message, settings.DEFAULT_FROM_EMAIL, [bidder_emails]),
			(winner_subject, winner_message, settings.DEFAULT_FROM_EMAIL, [winner_email]),
			)
		send_mass_mail(datatuple)

class BidEmail(models.Model):
	bid = models.ForeignKey("Bid", on_delete=models.PROTECT)


	def __str__(self):
		return self.bid


	def bid_created_email(self, bidder_emails):
		seller_email = self.bid.auction.seller.email
		context = {

				 	"seller": self.bid.auction.seller,
				 	"slug": self.bid.auction.slug,
				 	"title": self.bid.auction.title
				 }
		seller_message = render_to_string("seller_bid_registered.txt", context)
		bidder_message = render_to_string("bidder_bid_registered.txt", context)
		seller_subject = "New bid on your item"
		bidder_subject = "New bids registered"
		datatuple = (
			(seller_subject, seller_message, settings.DEFAULT_FROM_EMAIL, [seller_email]),
			(bidder_subject, bidder_message, settings.DEFAULT_FROM_EMAIL, [bidder_emails]),
			)
		send_mass_mail(datatuple)




