from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('student__username', 'course__title', 'body')
