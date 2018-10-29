def get_bidder_email(bids, seller_email):
	winner_amount = 0
	winner = ""
	bidder_email_list = []
	for items in bids:
		if items.user.email != seller_email:
			bidder_email_list.append(items.user.email)
		if items.bid_amount>winner_amount:
			winner_amount = items.bid_amount
			winner = items.user
			winner_email = items.user.email
	deduped_bidders_email =  list(set(bidder_email_list))
	bidder_email_str = ','.join(deduped_bidders_email)
	return winner,bidder_email_str