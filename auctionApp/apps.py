#for signals
from django.apps import AppConfig

class AuctionConfig(AppConfig):
    name = 'auctionApp'

    def ready(self):
        import auctionApp.signals







