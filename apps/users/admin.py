from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["nick_name", "birthday", "gender", "address", "mobile", "image"]
    search_fields = ["nick_name", "birthday", "gender", "address", "mobile", "image"]
    list_filter = ["nick_name", "birthday", "gender", "address", "mobile", "image"]

admin.site.register(UserProfile, UserProfileAdmin)