from django.contrib import admin
from app.models import ShortenedURL

class ShortenedURL_display(admin.ModelAdmin):
    list_display = ('user','original_url', 'short_url', 'created_at', 'has_ad','visitors')

admin.site.register(ShortenedURL, ShortenedURL_display)