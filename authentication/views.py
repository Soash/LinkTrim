from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from url_shortner import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from app.forms import URLShortenForm
from . tokens import generate_token
from django.contrib.auth.decorators import login_required

def home(request):
    form = URLShortenForm()
    if request.user.is_authenticated:
        fname = request.user.first_name
    else:
        fname = "Guest" 
    return render(request, 'authentication/home.html', {"fname":fname, "form":form, 'base_url': request.build_absolute_uri('/'),})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist!")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email Already Registered!")
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.is_active = False
        myuser.save()

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email - URL Shortner"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email],)
        email.fail_silently = True
        email.send()

        messages.success(request, "Your Account has been created succesfully. Please check you mail to activate it.")
        return redirect('home')

    return render(request, 'authentication/signup.html')

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Logged In Sucessfully!")
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')
    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')

def forgot(request):
    if request.method == "POST":
        email = request.POST['email']        
        if not User.objects.filter(email=email):
            messages.error(request, "Email Not Registered!")
            return redirect('signup')

        myuser = User.objects.get(email=email)
        # Reset Email
        current_site = get_current_site(request)
        email_subject = "Reset your password - URL Shortner"
        message2 = render_to_string('reset_mail.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email],)
        email.fail_silently = True
        email.send()

        messages.success(request, "Please check your mail to reset.")
        return redirect('forgot')
    else:
        return render(request, 'authentication/forgot.html')
    
def reset(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        return render(request, 'authentication/reset.html',{'username':myuser.username})
    else:
        return render(request,'reset_failed.html')

def savePass(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")
            return redirect('reset')
        try:
            user = User.objects.get(username=username)
            user.set_password(pass1)
            user.save()
            messages.success(request, "Password Changed!")
            return redirect('signin')
        except User.DoesNotExist:
            messages.error(request, "User not found!")
            return redirect('reset')
    else:
        return redirect('signin')
    

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        password = request.POST.get('password')

        # Check if the provided password is correct
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            # Password is correct, delete the account
            user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')  # Redirect to your home page or any other page
        else:
            # Password is incorrect
            messages.error(request, 'Incorrect password. Please try again.')

    return render(request, 'delete_account.html') 