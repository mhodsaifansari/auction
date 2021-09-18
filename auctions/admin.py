from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(groups)
admin.site.register(active_list)
admin.site.register(bids)
admin.site.register(comments)
admin.site.register(User)