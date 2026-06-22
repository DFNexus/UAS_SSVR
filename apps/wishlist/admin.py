from django.contrib import admin
from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'added_at')
    list_filter = ('course',)
    search_fields = ('student__username', 'course__title')
