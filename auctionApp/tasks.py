from __future__ import absolute_import

from celery.decorators import task

from celery.task.schedules import crontab
from celery.decorators import periodic_task
import pytz
from datetime import datetime, timedelta
from .models import Auction, Bid


def auction_due():
	auctions = Auction.objects.all()
	now = datetime.utcnow().replace(tzinfo=pytz.utc)
	for items in auctions:
		items.set_expired()


#@task(name="choose_winning_bidder")
@periodic_task(run_every=(crontab(minute='*/1')), name="choose_winning_bidder", ignore_result=True)
def choose_winner():
	auction_due()
	winner_amount = 0
	auctions = Auction.objects.filter(due = True, adjucated = False)
	if len(auctions)>0:
		for due_auction in auctions:
			slug = due_auction.slug
			bids = Bid.objects.filter(auction__slug = slug)
			for items in bids:
				if items.user != None:
					if items.bid_amount>winner_amount:
						winner_amount = items.bid_amount
						winner = items.user
						winner_email = items.user.email
				winner_amount = 0
				due_auction.adjucated = True
				due_auction.save()
	else:
		pass
