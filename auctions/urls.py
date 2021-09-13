from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from .views import *
from . import views


urlpatterns = [
    
    
    path("verify",TokenVerifyView.as_view(),name="check"),
    path("refresh",TokenRefreshView.as_view()),
    path("api/login",Login.as_view()),
    path("api/index",IndexView.as_view()),
    path("api/register",Register.as_view()),
    path("api/logout",Logout.as_view()),
    path("api/view_list/<int:id>",ViewListing.as_view()),
    path("api/comment/<int:id>",CommentView.as_view()),
    path("api/create_list",CreateListingView.as_view()),
    path("api/watchlist",WatchlistView.as_view()),
    path("api/set_watchlist/<int:id>",SetWatchlist.as_view()),
    path("api/cateogry",GroupView.as_view()),
    path("api/cateogry/<str:name>",GroupView.as_view()),
    path("api/close/<int:id>",closeView.as_view()),
    path("api/mylist",MylistView.as_view()),
    path("api/wonlist",WonView.as_view())   ,
    path("api/bid/<int:id>",BidView.as_view()),
    path("api/user/<str:username>",ProfileView.as_view()) 

]
