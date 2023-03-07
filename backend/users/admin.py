from django.contrib import admin

from .models import Follow, User

class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author", )
    empty_value_display = "-пусто-"

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email", )
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
