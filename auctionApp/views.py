# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.shortcuts import render, redirect , get_object_or_404, Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from auctionApp.models import Auction
from datetime import datetime, timedelta
import pytz 
from django.template.defaultfilters import slugify
from .forms import AuctionForm, AuctionUpdateForm, AuctionBidForm, ConfirmAuctionUpdateForm,ConfirmPostAuctionForm
from django.contrib import messages
from .models import Auction, Bid
from decimal import Decimal
from django.utils.timezone import utc
from django.utils import translation,timezone
from django.conf import settings
from  auctionApp.templatetags import PyExchangeRates
import json,ast
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.core import serializers
from django.contrib.auth import get_user_model
from auction.process_bidders import get_bidder_email
from accounts.models import UserProfile
from accounts.forms import UserProfileForm
from django.utils.timezone import activate

exchange = PyExchangeRates.Exchange('ef3866717fd64e9bad35a8d374cec92e')

def home(request):  
    if request.user.is_authenticated:
        lang = request.session.get('lang')
        lang_in_db = ""
        try:
            profile = UserProfile.objects.get(user=request.user)
            if lang and lang != None:
                profile.language_preference = lang
                profile.save()  
                lang_in_db = profile.language_preference
            else:
                pass
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
            if lang and lang != None:
                profile.language_preference = lang
                profile.save()  
                lang_in_db = profile.language_preference
            else:
                pass
        lang_in_db = profile.language_preference
        translation.activate(lang_in_db)
    auctions = Auction.objects.select_for_update()
    auctions = auctions.order_by('-timestamp')
    request.session['cur'] = "EUR"
    currency = request.session.get('cur')
    if request.POST.get("cur") == "eur":
        request.session['cur'] = "EUR"
        currency = request.session.get('cur')
    if request.POST.get("cur") == "usd":
        request.session['cur'] = "USD"
        currency = request.session.get('cur')
    if request.POST.get("cur") == "aud":
        request.session['cur'] = "AUD"
        currency = request.session.get('cur')
    if request.POST.get("lang") == "swedish":
        translation.activate('sv')
        request.session['lang'] = "sv"
        lang = request.session.get('lang')
        page_message = "Your language choice is Swedish"
        messages.success(request, _(page_message))
    if request.POST.get("lang") == "english":
        translation.activate('en-us')
        request.session['lang'] = "en-us"
        lang = request.session.get('lang')
        page_message = "Your language choice is English"
        messages.success(request, page_message) 
    template = 'list.html'
    context = {'auction': auctions, 'currency':currency,}
    return render(request,template,context)


def post_auction_view(request):
    if request.user.is_authenticated:
        auction_obj = Auction()
        form = AuctionForm((request.POST or None), instance = auction_obj)
        btn  = "Submit"
        system_deadline = datetime.utcnow().replace(tzinfo=pytz.utc)+timedelta(days = 2, hours=23, minutes=59) 
        if form.is_valid():
            new_auction = form.save(commit = False)
            user_deadline = new_auction.deadline
            diff = user_deadline - system_deadline
            minutes = divmod(diff.days * 86400 + diff.seconds, 60)
            minutes_left = minutes[0]
            if minutes_left >= 0:
                new_auction.previous_bid = new_auction.minimum_price
                new_auction.seller = request.user
                new_auction.slug = slugify(new_auction.title)
            else:
                messages.success(request, "More than a minute has passed since you wanted to post this auction. Deadline must be at least 3 days from today. Reload the page or add future date")
                context = {
                    "form":form,
                    "submit_btn": btn,
                    "deadline": user_deadline
                        }
                return render(request, "form.html", context)
            form = ConfirmPostAuctionForm((request.POST or None), instance=auction_obj)
            option = request.POST.get('option', '')
            request.session['option_form'] = "option_form"
            if option == "Yes":
                new_auction.save()
                form.save()
                page_message = "You have successful posted a new auction description"
                context = {"page_message": page_message}
                return render(request, "modify_complete.html", context)
            if option=="No":
                page_message = "You canceled, auction not posted"
                del request.session['option_form']
                context = {"page_message": page_message}
                return render(request, "modify_complete.html", context)
            sure = "Are you sure want to post this auction? Click Yes to continue"
            context = {
            "form":form, "submit_btn": btn, "confirm_message":sure
            }
            return render(request, "form.html", context)


        context = {
                    "form":form,
                    "submit_btn": btn,
                        }
        return render(request, "form.html", context)

    else:
        return HttpResponseRedirect('%s'%(reverse("auth_login")))


def bid_on_auction(request, slug):  
    if request.user.is_authenticated:
        #try:
            auction = Auction.objects.get(pk=slug)
            bidders = Bid.objects.all().filter(auction=auction)
            #print "all bidders are", bidders
            seller_email = auction.seller.email

            if auction.banned:
                page_message = "You cannot bid on Banned Auctions"
                context = {"page_message": page_message}
                return render(request, "modify_complete.html", context)
            else:
                bid = Bid() #New bid object
                bid.auction = auction #Assign auction to bid
                description = auction.description
                minimum_price = auction.minimum_price
                version = auction.d_version # version no for description
                version_for_bid = auction.bid_version# version no for bid
                old_version = request.session.get('d_version') #get from request the present version
                previous_bid_version = request.session.get('bid_version') #get from request the present version
                if auction.seller != request.user and not auction.banned:
                    form = AuctionBidForm((request.POST or None), instance=auction)
                    request.session['d_version'] = version
                    request.session['bid_version'] = version_for_bid #Save 1 in session
                    btn  = "Bid"
                    if form.is_valid():
                            bidding = form.save(commit = False)
                            latest_version = bidding.d_version
                            if old_version == None:
                                pass
                            if old_version != latest_version:
                                description = auction.description
                                messages.success(request, "Auction description has been updated since the last time")
                                context = {
                                "form":form, "submit_btn": btn, "description":description,
                                    }
                                return render(request, "form.html", context)
                            
                            latest_bid_version = bidding.bid_version
                            if previous_bid_version != latest_bid_version:
                                previous_bid = auction.previous_bid
                                #previous_bid = bid.previous_bid
                                messages.success(request, "New bids since the last time. Please resubmit a bid higher than (EUR)")
                                context = {
                                    "form":form, "submit_btn": btn, "minimum_price":previous_bid,
                                    }
                                return render(request, "form.html", context)
                            else:
                                if ((bidding.bid_price>auction.previous_bid) == True) and (bidding.bid_price>auction.minimum_price):
                                    deadline = bidding.deadline
                                    now = datetime.utcnow().replace(tzinfo=pytz.utc)
                                    diff = (deadline - now)
                                    print("diff is", diff)
                                    minutes = divmod(diff.days * 86400 + diff.seconds, 60)
                                    minutes_left = minutes[0]
                                    print("minutes left", minutes_left)
                                    new_deadline = deadline+timedelta(days = 0, hours = 0, minutes =5)
                                    bidding.previous_bid = bidding.bid_price
                                    bid.user = request.user
                                    bid.bid_amount = bidding.bid_price
                                    #bid.previous_bid = bidding.bid_price
                                    if minutes_left <= 5:
                                        bidding.deadline = deadline+timedelta(days = 0, hours = 0, minutes =5)
                                        pass
                                    bidding.save()
                                    bidding.bid_version = bidding.bid_version + 1
                                    form.save()
                                elif (bidding.bid_price<=auction.minimum_price):
                                    minimum_price = auction.minimum_price
                                    #previous_bid = bid.previous_bid
                                    messages.success(request, "New bids must be greater than Minimum price of (EUR)")
                                    context = {
                                    "form":form, "submit_btn": btn,"minimum_price":minimum_price,
                                    }
                                    return render(request, "form.html", context)
                                else:
                                    previous_bid = auction.previous_bid
                                    messages.success(request, "New bids must be greater than the previous bid of (EUR)")
                                    context = {
                                    "form":form, "submit_btn": btn,"minimum_price":previous_bid,
                                    }
                                    return render(request, "form.html", context)
                            bid.save()
                            #Get winning bidder here and the list of all bidders on the current auction
                            winner, list_of_bidders_email = get_bidder_email(bidders, seller_email)
                            auction.current_winning_bidder = winner.username
                            auction.save()

                            page_message = "You have placed a new bid"
                            context = {"page_message": page_message}
                            return render(request, "modify_complete.html", context)
                    context = {
                    "form":form, "submit_btn": btn, "description":description,
                        }
                    return render(request, "form.html", context)
                else:
                    page_message = "You cannot bid on own auctions"
                    context = {"page_message": page_message}
                    return render(request, "modify_complete.html", context)
        #except :
                #raise Http404
    else:
        return HttpResponseRedirect('%s'%(reverse("auth_login")))
        ##return redirect("auth_login")

def single_auction(request, slug):

    try:
        auction = Auction.objects.get(slug = slug)
        form = AuctionUpdateForm((request.POST or None), instance=auction)
        btn  = "Modify Auction"
        #request.session['slug_for_description'] = slug
        if form.is_valid():
                    new_user = form.save(commit = False)
                    #Get the current description version
                    form = ConfirmAuctionUpdateForm((request.POST or None), instance=auction)
                    option = request.POST.get('option', '')
                    request.session['option_form'] = "option_form"
                    if option == "Yes":
                        new_user.save()
                        new_user.d_version = new_user.d_version + 1
                        form.save()
                        del request.session['option_form']
                        page_message = "You have successful updated your auction description"
                        context = {"page_message": page_message}
                        return render(request, "modify_complete.html", context)
                    if option=="No":
                        page_message = "You canceled, description not modified"
                        del request.session['option_form']
                        context = {"page_message": page_message}
                        return render(request, "modify_complete.html", context)

        sure = "Are you sure want to update description? Click Yes to continue"
        context = {
        "form":form, "submit_btn": btn, "confirm_message":sure
            }
        return render(request, "form.html", context)
    except :
        raise Http404


def seller_view(request):
    if request.user.is_authenticated:
        seller = request.user
        auction = Auction.objects.all().filter(seller = seller)
        template = 'seller.html'
        context = {'auction': auction}
        return render(request,template,context)
    else:
        return HttpResponseRedirect('%s'%(reverse("auth_login")))


def search(request):
    try:
        q = request.GET.get('q')
    except:
            q = None
    if q:
        auctions = Auction.objects.filter(title__icontains = q)
        context ={'query': q, 'auction': auctions}
        template = 'results.html'
    else:   
        template = 'list.html'
        context ={}
    return render(request, template, context)


def translate_view(request):
    print(translation.get_language())
    if request.POST.get("lang") == "swedish":
        translation.activate('sv')
        request.session['lang'] = "sv"
        print(request.session.get('lang'))
        page_message = ("Your language preference is now swedish")
        print(page_message)
        context = {"page_message": page_message}
        return render(request, "translation.html", context)
    if request.POST.get("lang") == "english":
        translation.activate('en-us')
        request.session['lang'] = "en-us"
        print(request.session.get('lang'))
        page_message = "Your language preference is now English"
        context = {"page_message": page_message}
        return render(request, "translation.html", context)
