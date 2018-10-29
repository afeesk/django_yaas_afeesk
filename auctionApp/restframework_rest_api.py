from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.shortcuts import get_object_or_404

from auctionApp.models import Auction
from auctionApp.serializers import AuctionResourceGetSerializer

@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer,])
def auction_list(request,):
    auctions = Auction.objects.all()
    serializer = AuctionResourceGetSerializer(auctions, many=True)
    return Response(serializer.data)


class AuctionDetail(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        auctions = get_object_or_404(Auction, id=id)
        serializer = BlogDetailSerializer(auctions)
        return Response(serializer.data)

class AuctionSearch(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug):
        auction = get_object_or_404(auction, slug=slug)
        serializer = auctionDetailSerializer(auction)
        return Response(serializer.data)


class auctionBid(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        auction = get_object_or_404(auction, pk=pk)
        serializer = auctionDetailSerializer(auction)
        return Response(serializer.data)

    def post(self, request, pk):
        auction = get_object_or_404(auction, pk=pk)
        data = request.data
        print(request.data)
        serializer = auctionDetailSerializer(auction, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


