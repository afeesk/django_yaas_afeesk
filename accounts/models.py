from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.db import models
from django.template.loader import render_to_string
from auctionApp.models import Auction

#from .signals import get_or_create_stripe

#Foreign key allows multiple
#One to one does only one
class UserProfile(models.Model):  
	user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, on_delete=models.PROTECT)
	language_preference = models.CharField(max_length=140)  
	#mem = models.CharField(max_length=140)

	def __str__(self):
		return 'Profile of user: %s' % self.user.username


class EmailConfirmed(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	auction = models.ForeignKey(Auction, null=True, blank= True, on_delete=models.PROTECT)
	activation_key = models.CharField(max_length = 200)
	confirmed = models.BooleanField(default = False)

	def __str__(self):
		return self.confirmed

	def activate_user_email(self):
		#send email here and render a string
		 #user.emailedconfirmed.email_user()
		 activation_url = "%s%s" %(settings.SITE_URL, reverse("activation_view", args = [self.activation_key]))
		 context = {
		 	"activation_key":self.activation_key,
		 	"activation_url":activation_url,
		 	"user": self.user.username

		 }
		 message = render_to_string("activation_message.txt", context)
		 subject = "Activate your email"
		 self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

	def email_user(self, subject, message, from_email=None, **kwargs):
		fail_silently = True
		#send_mail(subject, message, from_email, [self.user.email], **kwargs)
		send_mail(subject, message, from_email, [self.user.email], kwargs)
