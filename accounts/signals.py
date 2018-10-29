import random
import hashlib
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from .models import EmailConfirmed

User = get_user_model()


def user_created_receiver(sender, instance, created, *args, **kwargs):
		user = instance
		if created:
			email_confirmed, email_is_created = EmailConfirmed.objects.get_or_create(user =user)
			if email_is_created:
				short_hash = hashlib.sha1(str.encode(str(random.random()))).hexdigest()[:5]
				username = user.username
				base, domain = str(user.email).split("@")
				activation_key = hashlib.sha1(str.encode(short_hash+base)).hexdigest()
				email_confirmed.activation_key = activation_key
				email_confirmed.save()
				email_confirmed.activate_user_email()

				
post_save.connect(user_created_receiver, sender = User)