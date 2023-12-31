import string
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import URLShortenForm
from .models import ShortenedURL

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(6))

@login_required(login_url='signin')
def shorten_url(request):
    if request.method == 'POST':
        form = URLShortenForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['original_url']
            short_url = generate_short_url()

            while ShortenedURL.objects.filter(short_url=short_url).exists():
                short_url = generate_short_url()

            shortened_url = ShortenedURL.objects.create(
                user=request.user,
                original_url=original_url,
                short_url=short_url
            )
            return redirect('dashboard')
    else:
        return redirect('home')

@login_required(login_url='signin')
def custom_shorten_url(request):
    if request.method == 'POST':
        form = URLShortenForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['original_url']
            short_url = request.POST['custom_url']

            shortened_url = ShortenedURL.objects.create(
                user=request.user,
                original_url=original_url,
                short_url=short_url
            )
            return redirect('dashboard')
    else:
        return redirect('home')

@login_required(login_url='signin')
def dashboard(request):
    form = URLShortenForm()
    user_urls = ShortenedURL.objects.filter(user=request.user).order_by('-created_at')

    context = {'user_urls': user_urls,
               'base_url': request.build_absolute_uri('/'),
               'form': form,
            }
    return render(request, 'dashboard.html', context=context)

def redirect_to_original(request, short_url):
    try:
        short_url_obj = ShortenedURL.objects.get(short_url=short_url)
        original_url = short_url_obj.original_url
        has_ad = short_url_obj.has_ad
        visitors = short_url_obj.visitors + 1
        short_url_obj.visitors = visitors
        short_url_obj.save()
        if has_ad:
            return render(request, 'ad.html', {'original_url': original_url})
        else:
            return redirect(original_url)
    except ShortenedURL.DoesNotExist:
        return render(request, '404.html')

@login_required(login_url='signin')
def delete(request, short_url):
    url = ShortenedURL.objects.get(short_url=short_url)
    url.delete()
    return redirect('dashboard')

@login_required(login_url='signin')
def hasAd(request, short_url):
    url = ShortenedURL.objects.get(short_url=short_url)
    if url.has_ad:
        url.has_ad = False
    else:
        url.has_ad = True
    url.save()
    return redirect('dashboard')


def custom_404(request, exception):
    return render(request, '404.html', status=404)