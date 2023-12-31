from django.db import models
from django.contrib.auth.models import User

class ShortenedURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_url = models.URLField()
    short_url = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    has_ad = models.BooleanField(default=False)
    visitors = models.IntegerField(default=0)

    def __str__(self):
        return self.short_url
