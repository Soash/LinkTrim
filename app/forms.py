from django import forms
from .models import ShortenedURL

class URLShortenForm(forms.ModelForm):
   class Meta:
       model = ShortenedURL
       fields = ['original_url']

   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields['original_url'].label = ''
       self.fields['original_url'].widget.attrs['placeholder'] = 'Enter your URL'
