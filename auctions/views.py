from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from auctions.serializers import *
from django.db import IntegrityError
from django.db.models import Max
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.middleware.csrf import get_token
from django.core.paginator import Paginator

class Register(APIView):
    def post(self,request,*args,**kwargs):
        username = request.data["username"]
        email = request.data["email"]

        # Ensure password matches confirmation
        password = request.data["password"]
        confirmation = request.data["confirmation"]
        if password != confirmation:
            return Response( {
                "message": "Passwords must match."
            },status=400)

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return Response( {
                "message": "Username already taken."
            },status=401)
        
        return Response("User successfully created")

class Login(TokenObtainPairView):
    serializer_class=UserTokenObtain
    

class Logout(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        refresh=RefreshToken.for_user(request.user)
        return Response("Logout successful")
class IndexView(APIView):
    def get(self,request,*args,**kwargs):
        bids_data=active_list.objects.filter(status=True).order_by('-id')
        page=1
        paginator=Paginator(bids_data,10)
        try:
            page=request.GET["page"]
            
        except:
            print("page is not there")
        bids_data=paginator.page(page)
        bids_list=get_bid_data(bids_data)    
        bids_data=ActiveLisiting(bids_data,many=True)
        return Response({'listing':bids_data.data,'bid_list':bids_list,'max_page':paginator.num_pages})
class ViewListing(APIView):
    permissions_classes=[IsAuthenticated|AllowAny]
    def get(self,request,*args,**kwargs):
        try:
            id=kwargs.get('id')
            listing_data=active_list.objects.get(pk=id)
            watchlist=False
            close_permit=False
            if(request.user.id!=None):
                
                if(request.user.watchlists.filter(id=listing_data.id).exists()):
                    watchlist=True
                if(request.user==listing_data.owner):
                    close_permit=True
            comments=listing_data.comment_by_users.all()
            comments=comment_serializer(comments,many=True)
            bid_data=get_bid_data([listing_data])
            listing_data=ViewList(listing_data)
            
            return Response({'listing':listing_data.data,'bid_data':bid_data[0],'comments':comments.data,'is_in_watchlist':watchlist,'close_permit':close_permit})
        except:
            return Response({"message":"Bad value for this endpoint"},status=404)
class CommentView(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        try:
            current_list=active_list.objects.get(pk=kwargs.get('id'))
            comment_data=comments(text=request.data["comment_text"],comment_by=request.user,comment_on=current_list)     
            comment_data.save()
            return Response("Saved Success")
        except:
            return Response({"message":"Bad value for this endpoint"},status=404)
class CreateListingView(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        try:
            image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png"
            if request.data["image"] != "":
                    image = request.data["image"]
            if request.data["group"] == "None":
                listing = active_list(title=request.data["title"],description=request.data["description"],owner=request.user,primary_bid=request.data["bid"],image=image)
            else:
                group=groups.objects.get(id=int(request.data["group"]))
                listing = active_list(title=request.data["title"],description=request.data["description"],owner=request.user,primary_bid=request.data["bid"],belongs_to=group,image=image)
            listing.save()
            return Response("Saved",status=200)    
        except:
            return Response("Isssue occured",status=400)
class WatchlistView(APIView):
    permission_classes=(IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        watchlist_list=request.user.watchlists.all().order_by('-id')
        page=1
        paginator=Paginator(watchlist_list,10)
        try:
            page=request.GET["page"]
            
        except:
            print("page is not there")
        watchlist_list=paginator.page(page)
        bid_data=get_bid_data(watchlist_list)
        watchlist_list=ActiveLisiting(watchlist_list,many=True)
       
        return Response({'listing':watchlist_list.data,'bid_list':bid_data,'max_page':paginator.num_pages})
class SetWatchlist(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        id=kwargs.get('id')
        listing_data=active_list.objects.get(pk=id)
        if(request.user.watchlists.filter(id=listing_data.id).exists()):
                request.user.watchlists.remove(listing_data)
                return Response("Lisiting has been removed")
        request.user.watchlists.add(listing_data)
        return Response("Lisiting has been added")
class GroupView(APIView):
    def get(self,request,*args,**kwargs):
        if(kwargs.get('name')==None):
            groups_list=groups.objects.all()
            groups_list=group_serializer(groups_list,many=True)
            return Response(groups_list.data)
        else:
            listing_in_group=active_list.objects.filter(status=True,belongs_to=groups.objects.get(text=kwargs.get("name")))
            page=1
            paginator=Paginator(listing_in_group,10)
            try:
                page=request.GET["page"]
        
            except:
                print("page is not there")
            listing_in_group=paginator.page(page)
            bid_data=get_bid_data(listing_in_group)
            listing_in_group=ActiveLisiting(listing_in_group,many=True)
            
            return Response({'listing':listing_in_group.data,'bid_list':bid_data,'max_page':paginator.num_pages})
class closeView(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        listing = active_list.objects.get(pk=kwargs.get('id'))
        if request.user==listing.owner:
            listing.status=False
            try:
                bid_data=bids.objects.filter(placed_on=listing).aggregate(Max('bid'))["bid__max"]
                bid_data=bids.objects.get(placed_on=listing,bid=bid_data)
            except bids.DoesNotExist:
                bid_data=None
            if bid_data is None:
                bid_data=bids(placed_on=listing,bid=listing.primary_bid,bidded_by=listing.owner)
                bid_data.save()
            
            listing.won_by=bid_data
            listing.save()
            return Response("saved")
class MylistView(APIView):
    permission_classes=(IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        watchlist_list=active_list.objects.filter(owner=request.user).order_by('-id')
        page=1
        paginator=Paginator(watchlist_list,10)
        try:
            page=request.GET["page"]
            
        except:
            print("page is not there")
        watchlist_list=paginator.page(page)
        bid_data=get_bid_data(watchlist_list)
        watchlist_list=ActiveLisiting(watchlist_list,many=True)
        return Response({'listing':watchlist_list.data,'bid_list':bid_data,'max_page':paginator.num_pages})
class WonView(APIView):
    permission_classes=(IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        won_list=[]
        for bid_list in bids.objects.filter(bidded_by=request.user):
            won_list+=active_list.objects.filter(won_by=bid_list)
        page=1
        paginator=Paginator(won_list,3)
        try:
            page=request.GET["page"]
            
        except:
            print("page is not there")
        won_list=paginator.page(page)
        bid_list=get_bid_data(won_list)
        won_list=ActiveLisiting(won_list,many=True)
        
        return Response({'listing':won_list.data,'bid_list':bid_list,'max_page':paginator.num_pages})

class BidView(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        
        listing_data=active_list.objects.get(pk=kwargs.get('id'))
        
        if listing_data.status==True:
            bid_data=listing_data.primary_bid
            if int(request.data["bid"])>bid_data:
                bid=bids(placed_on=listing_data,bid=int(request.data["bid"]),bidded_by=request.user)    
                bid.save()
                return Response("Successfully placed")
            else:
                return Response("Bid need to be greater then intial bid")
        else:
            return Response("Bid is closed",status=403)
class ProfileView(APIView):
    permission_classes=(IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        user_data=User.objects.get(username=kwargs.get('username'))
        owned_list=active_list.objects.filter(owner=user_data)
        page=1
        paginator=Paginator(owned_list,10)
        try:
            page=request.GET["page"]
            
        except:
            print("page is not there")
         
        owned_list=paginator.page(page)
        bid_list=get_bid_data(owned_list)
        watchlist_list=ViewList(owned_list,many=True)
        
        return Response({'username':user_data.username,'watchlist':watchlist_list.data,'bid_list':bid_list,'max_page':paginator.num_pages})
def get_bid_data(objects_list):
    bid_data=[]
    for objects in objects_list:
        try:
            bid_data_temp=bids.objects.filter(placed_on=objects).aggregate(Max('bid'))["bid__max"]
        except bids.DoesNotExist:
            bid_data_temp=None
        if bid_data_temp is None:
            bid_data_temp=objects.primary_bid
        bid_data+=[bid_data_temp]
    return bid_data

