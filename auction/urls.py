from django.urls import re_path, include
from auctionApp.views import *
from accounts.views import *
from auctionApp.restframework_rest_api import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = (


    re_path(r'^admin/', admin.site.urls),
    re_path(r'api/auctions/', auction_list),
    re_path(r'api/auctions/(?P<id>\d+)/', AuctionDetail.as_view()),
    re_path(r'api/auctions/(?P<slug>[\w-]+)/', AuctionSearch.as_view()),
    re_path('api/auctions/bid/<int:pk>/', auctionBid.as_view()),
    re_path(r'^$', home, name='home'),
    re_path(r'^s/$', search, name='search'),
    re_path(r'^accounts/activate/(?P<activation_key>\w+)/$', activation_view, name='activation_view'),
    re_path(r'^accounts/logout/$', logout_view, name='auth_logout'),
    re_path(r'^accounts/login/$', login_view, name='auth_login'),
    re_path(r'^accounts/register/$', registration_view, name='auth_register'),
    re_path(r'^accounts/modify/$', modify_view, name='modify_view'),
    re_path(r'^auctions/post/$', post_auction_view, name='post_auction_view'),
    re_path(r'^auctions/seller/(?P<slug>[\w-]+)/$', single_auction, name='single_auction'),
    re_path(r'^bid/(?P<slug>[\w-]+)/$', bid_on_auction, name='bid_on_auction'),
    re_path(r'^auctions/seller/$', seller_view, name='seller_view'),
   
    )

