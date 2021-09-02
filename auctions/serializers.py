
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import *
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class User_serializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username']
class ActiveLisiting(serializers.ModelSerializer):
    class Meta:
        model=active_list
        fields=['id','title','description','primary_bid','image']
class ViewList(serializers.ModelSerializer):
    owner=User_serializer(read_only=True)
    class Meta:
        model=active_list
        fields=['id','title','description','owner','image','belongs_to','won_by','status']
class BidData(serializers.ModelSerializer):
    class Meta:
        model=bids
        fields=['id','bid']
class comment_serializer(serializers.ModelSerializer):
    class Meta:
        model=comments
        fields=['text','comment_by']
class group_serializer(serializers.ModelSerializer):
    class Meta:
        model=groups
        fields=['id','text']
class UserTokenObtain(TokenObtainPairSerializer):
    def validate(self, attrs):
        data=super().validate(attrs)
        refresh=self.get_token(self.user)
        data['refresh']=str(refresh)
        data['access']=str(refresh.access_token)
        data['user']=self.user.username
        data['id']=self.user.id
        return data
class NewListing_serializer(serializers.ModelSerializer):
    class Meta:
        model=active_list
        fields=['title','description']