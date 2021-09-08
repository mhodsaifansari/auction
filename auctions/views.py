from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.settings import perform_import
from rest_framework_simplejwt.views import TokenObtainPairView
from auctions.serializers import *
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max, expressions
from .models import *
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.middleware.csrf import get_token
def csrf(request):
    return JsonResponse({'csrfToken':get_token(request)})
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
        
        bids_list=get_bid_data(bids_data)    
        bids_data=ActiveLisiting(bids_data,many=True)
        return Response({'listing':bids_data.data,'bid_list':bids_list})
class ViewListing(APIView):
    permissions_classes=[IsAuthenticated|AllowAny]
    def get(self,request,*args,**kwargs):
        
        id=kwargs.get('id')
        listing_data=active_list.objects.get(pk=id)
        
        watchlist=False
        close_permit=False
        print(request.user)
        if(request.user.id!=None):
            
            if(request.user.watchlists.filter(id=listing_data.id).exists()):
                watchlist=True
            if(request.user==listing_data.owner):
                close_permit=True
        print(watchlist)
        print(close_permit)
        comments=listing_data.comment_by_users.all()
        comments=comment_serializer(comments,many=True)
        bid_data=get_bid_data([listing_data])
        print(bid_data[0])
        listing_data=ViewList(listing_data)
        
        return Response({'listing':listing_data.data,'bid_data':bid_data[0],'comments':comments.data,'is_in_watchlist':watchlist,'close_permit':close_permit})
        
        """
        if request.user == listing_data.owner:
        
            close_option = True
            
        else:
            close_option=False
            
        if request.user.is_authenticated: 
            watchlist_list=request.user.watchlists.all()
        else:
        watchlist_list=None
        
        if request.method=="POST":
                if int(request.POST["bid"])>bid_data:
                    bid=bids(placed_on=listing_data,bid=int(request.POST["bid"]),bidded_by=request.user)
                    
                    bid.save()
                    return HttpResponseRedirect(reverse("listing_page",args=(id,)))
                else:
                    message="Bid needs to be bigger then current Bid"


        
        return render(request,"auctions/view_list.html",{
            "listing_details":listing_data,
            "comments_list":listing_data.comment_by_users.all(),
            "message":message,
            "bid_data":bid_data,
            "close_option":close_option,
            "watchlist_list":watchlist_list
        })"""
        
class CommentView(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request,*args,**kwargs):
        #try:
        current_list=active_list.objects.get(pk=kwargs.get('id'))
        comment_data=comments(text=request.data["comment_text"],comment_by=request.user,comment_on=current_list)     
        comment_data.save()
        return Response("Saved Success")
        # except:
        #     return Response("Issue")

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
        watchlist_list=request.user.watchlists.all()
        print(watchlist_list)
        bid_data=get_bid_data(watchlist_list)
        watchlist_list=ActiveLisiting(watchlist_list,many=True)
       
        return Response({'listing':watchlist_list.data,'bid_list':bid_data})
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
        """"
        if name is None:
        print(groups.objects.all())
        return render(request,"auctions/catogery.html",{
            "group_lists":groups.objects.all(),
            "grouplist":True
        })
    else:
        group=groups.objects.get(text=str(name))
        bids_data=get_bid_data(active_list.objects.filter(status=True,belongs_to=group))
        return render(request,"auctions/catogery.html",{
            "item_lists":group.items.filter(status=True),
            "group":group,
            "bids":bids_data,
            "grouplist":False
        })"""
        if(kwargs.get('name')==None):
            groups_list=groups.objects.all()
            groups_list=group_serializer(groups_list,many=True)
            return Response(groups_list.data)
        else:
            listing_in_group=active_list.objects.filter(status=True,belongs_to=groups.objects.get(text=kwargs.get("name")))
            bid_data=get_bid_data(listing_in_group)
            listing_in_group=ActiveLisiting(listing_in_group,many=True)
            
            return Response({'listing':listing_in_group.data,'bid_list':bid_data})
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
        watchlist_list=active_list.objects.filter(owner=request.user)
        bid_data=get_bid_data(watchlist_list)
        watchlist_list=ActiveLisiting(watchlist_list,many=True)
        print(watchlist_list.data)
        return Response({'listing':watchlist_list.data,'bid_list':bid_data})
class WonView(APIView):
    permission_classes=(IsAuthenticated,)
    def get(self,request,*args,**kwargs):
        won_list=[]
        for bid_list in bids.objects.filter(bidded_by=request.user):
            won_list+=active_list.objects.filter(won_by=bid_list)
        bid_list=get_bid_data(won_list)
        won_list=ActiveLisiting(won_list,many=True)
        
        return Response({'listing':won_list.data,'bid_list':bid_list})

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
        user_data=User.objects.get(id=kwargs.get('id'))
        owned_list=active_list.objects.filter(owner=user_data)
        print(owned_list)
        bid_list=get_bid_data(owned_list)
        watchlist_list=ViewList(owned_list,many=True)
        
        return Response({'username':user_data.username,'watchlist':watchlist_list.data,'bid_list':bid_list})
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
        print(bid_data)
    return bid_data

def index(request):
    bids_data=get_bid_data(active_list.objects.filter(status=True))
    if request.user.is_authenticated: 
        watchlist_list=request.user.watchlists.all()
    else:
       watchlist_list=None
    
    return render(request, "auctions/index.html",{
            "active_lists":active_list.objects.filter(status=True),
            "bids":bids_data,
            "watchlist_list":watchlist_list
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_list(request):
    if request.method == "POST":
        
        
        
        if request.POST["image"] == '':
            image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png"
        else:
            image=request.POST["image"]
        if request.POST["group"] == "None":
            listing = active_list(title=request.POST["title"],description=request.POST["description"],owner=request.user,primary_bid=request.POST["bid"],image=image)
        else:
            group=groups.objects.get(id=int(request.POST["group"]))
            listing = active_list(title=request.POST["title"],description=request.POST["description"],owner=request.user,primary_bid=request.POST["bid"],belongs_to=group,image=image)
        listing.save()
        
        return HttpResponseRedirect(reverse("index"))
    
    return render(request,"auctions/create_list.html",{
        "group_list":groups.objects.all()
    })

def listing_page(request,id):
    listing_data=active_list.objects.get(pk=int(id))
    message=None
    try:
        bid_data=bids.objects.filter(placed_on=listing_data).aggregate(Max('bid'))["bid__max"]
    except bids.DoesNotExist:
        bid_data=None
    if bid_data is None:
            bid_data=listing_data.primary_bid
    
    if request.user == listing_data.owner:
       
        close_option = True
        
    else:
        close_option=False
        
    if request.user.is_authenticated: 
        watchlist_list=request.user.watchlists.all()
    else:
       watchlist_list=None
    
    if request.method=="POST":
            if int(request.POST["bid"])>bid_data:
                bid=bids(placed_on=listing_data,bid=int(request.POST["bid"]),bidded_by=request.user)
                
                bid.save()
                return HttpResponseRedirect(reverse("listing_page",args=(id,)))
            else:
                message="Bid needs to be bigger then current Bid"


    
    return render(request,"auctions/view_list.html",{
        "listing_details":listing_data,
        "comments_list":listing_data.comment_by_users.all(),
        "message":message,
        "bid_data":bid_data,
        "close_option":close_option,
        "watchlist_list":watchlist_list
     })

def comment_view(request,id):
    if request.method == "GET":
        return HttpResponseRedirect(reverse(index))
    elif request.method =="POST":
        current_list=active_list.objects.get(pk=int(id))
        comment_data=comments(text=request.POST["comment_text"],comment_by=request.user,comment_on=current_list)
        comment_data.save()
        return HttpResponseRedirect(reverse("listing_page",args=(id,)))

def watchlist_view(request):
    watchlist_list=request.user.watchlists.all()
    if request.method == "POST":
        if request.POST["todo"] == str("add"):
            watchlist_object=request.user.watchlists.add(active_list.objects.get(pk=int(request.POST["id"])))
        elif str(request.POST["todo"]) == str("remove"):
            watchlist_object=active_list.objects.get(pk=int(request.POST["id"]))
            request.user.watchlists.remove(watchlist_object)
        
            
        return HttpResponseRedirect(reverse("listing_page",args=(request.POST["id"],)))
    
    return render(request,"auctions/watchlist.html",{
        "watchlists":watchlist_list
    })

def cateogry(request,name=None):
    if name is None:
        print(groups.objects.all())
        return render(request,"auctions/catogery.html",{
            "group_lists":groups.objects.all(),
            "grouplist":True
        })
    else:
        group=groups.objects.get(text=str(name))
        bids_data=get_bid_data(active_list.objects.filter(status=True,belongs_to=group))
        return render(request,"auctions/catogery.html",{
            "item_lists":group.items.filter(status=True),
            "group":group,
            "bids":bids_data,
            "grouplist":False
        })

def close(request,id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            listing = active_list.objects.get(pk=int(id))
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

    return HttpResponseRedirect(reverse(index))

def mylist(request):
    bids_data=get_bid_data(active_list.objects.filter(owner=request.user))
    if request.user.is_authenticated: 
        watchlist_list=request.user.watchlists.all()
    else:
        watchlist_list=None
    
    return render(request, "auctions/mylist.html",{
            "active_lists":active_list.objects.filter(owner=request.user),
            "bids":bids_data,
            "watchlist_list":watchlist_list
        })

def wonlist(request):
    won_list=[]
    for bid_list in bids.objects.filter(bidded_by=request.user):
        won_list+=active_list.objects.filter(won_by=bid_list)
    
    return render(request,"auctions/won_list.html",{
        "wonlists":won_list
    })