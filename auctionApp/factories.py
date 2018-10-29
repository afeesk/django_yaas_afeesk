import factory
from django.conf import settings
from django.utils.timezone import utc
import datetime
from django.contrib.auth.hashers import make_password


from auctionApp.models import Auction
from accounts.models import UserProfile
from django.contrib.auth.models import User
import factory.fuzzy


class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = User
	#FACTORY_HIDDEN_ARGS = ('language_preference',)

	username = factory.Sequence(lambda n: 'username{0}'.format(n))
	email = factory.Sequence(lambda n: 'username{0}@gmail.com'.format(n))
	password = make_password("password")
	is_active = True
	#language_preference = factory.Iterator(['Swedish', 'English'])
		


class AuctionFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Auction

	seller = factory.SubFactory(UserFactory)
	title = factory.Sequence(lambda n: 'This is auction number{0}'.format(n))
	description = factory.Sequence(lambda n: 'Here goes the description for auction {0}'.format(n))
	#minimum_price = factory.Sequence(lambda n: int'{0}' + 1.format(n))
	#minimum_price = factory.Faker(0.5, 42.7, 3)
	minimum_price = 0.01
	d_version = 0
	bid_version = 0
	previous_bid = 0
	bid_price = 0
	timestamp = factory.LazyAttribute(lambda o: datetime.datetime.utcnow())
	deadline = factory.LazyAttribute(lambda o: o.timestamp + datetime.timedelta(days=3))
	active = True
	banned = False
	due = False
	adjucated = False
	slug = factory.Sequence(lambda n: 'auction{0}_slug'.format(n))
