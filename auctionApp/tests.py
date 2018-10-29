import pytest
from django.shortcuts import redirect
from django.urls import reverse
#from model_mommy import mommy
from django.test import TestCase
from auctionApp.models import Auction
from django.contrib.auth.models import User
from django.test import RequestFactory
from accounts.views import login_view
from auctionApp.factories import AuctionFactory, UserFactory
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages  
#from accounts.views import login_view

@pytest.mark.django_db
class TestAuction(TestCase):

    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['auction']), 0)



    def test_create_auction(self):
        auction = AuctionFactory.create()
        auction = AuctionFactory.create()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['auction']) , 2)
        self.assertEqual(auction.title, "This is auction number2")
        self.assertEqual(auction.description, "Here goes the description for auction 2")

    
    def test_user_login_client(self):
        auction = AuctionFactory.create()
        response = self.client.login(username = auction.seller, password = "password")
        self.assertTrue(response)
        self.client.logout()
    
    def test_login_home_view(self):            
        auction = AuctionFactory.create()
        request_factory = RequestFactory()
        request = request_factory.post('/accounts/login/', data={'username': auction.seller, 'password':"password"})
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        middleware = SessionMiddleware()
        middleware.process_request(request)
        response = login_view(request)

    def test_authenticated_to_bid(self):
        auction = AuctionFactory.create()
        request_factory = RequestFactory()
        request = request_factory.post('/auctions/post/', data={'username': auction.seller, 'password':"password1"})
           

    