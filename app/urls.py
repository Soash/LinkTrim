from django.urls import path
from . import views

urlpatterns = [
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('cshorten/', views.custom_shorten_url, name='cshorten_url'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<str:short_url>/', views.redirect_to_original, name='redirect_to_original'),
    path('dashboard/<str:short_url>/delete/', views.delete, name='delete'),
    path('dashboard/<str:short_url>/ad/', views.hasAd, name='hasAd'),
]
