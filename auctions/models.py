from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlists=models.ManyToManyField("active_list",blank=True,related_name="watched_by")
    def __str__(self):
        return f"{self.username}"
        
class active_list(models.Model):
    title=models.CharField(max_length=64)
    description=models.TextField()
    owner=models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="active_list")
    primary_bid=models.IntegerField()
    image=models.URLField(default="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png")
    belongs_to=models.ForeignKey("groups",on_delete=models.DO_NOTHING,related_name="items",blank=True,null=True)
    status=models.BooleanField(default=True)
    won_by=models.ForeignKey("bids",on_delete=models.DO_NOTHING,related_name="won",blank=True,null=True)
    
    def __str__(self):
        return f"title:{self.title}"
    def serialize(self):
        return {'title':self.title}
    
class bids(models.Model):
    placed_on=models.ForeignKey(active_list,on_delete=models.CASCADE,related_name="bids")
    bid=models.IntegerField()
    bidded_by=models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="bidding")
    def __str__(self):
        return f"{self.placed_on}: {self.bid} by {self.bidded_by}"

class comments(models.Model):
    text=models.TextField()
    comment_by=models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="comment")
    comment_on=models.ForeignKey(active_list,on_delete=models.CASCADE,related_name="comment_by_users")
    def __str__(self):
        return f"{self.comment_by}: {self.text}  (comment on {self.comment_on})"

class groups(models.Model):
    text=models.TextField()
    def __str__(self):
        return f"{self.text}"


    