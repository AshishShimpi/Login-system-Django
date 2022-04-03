
from base64 import urlsafe_b64decode
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from auth.tocken import generate_token

# Create your views here.
def home(request):
    return render(request,"home.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['Cpassword']

        if User.objects.filter(username = username):
            messages.error(request, 'Username already exists!. Please try different Username.')
            return redirect("home")

        if User.objects.filter(email = email):
            messages.error(request, 'Email already registered!. Please use different Email.')
            return redirect("home")

        if cpassword != password:
            messages.error(request, 'Passwords must be same.')
            return redirect("home")

        if len(username)>=8:
            messages.error(request, 'Username must be greater than 8 characters.')
            return redirect("home")
        
        if not username.isalnum():
            messages.error(request, 'Username must be alpha numeric.')
            return redirect("home")
        


        newUser = User.objects.create_user(username, email, password)
        newUser.first_name = fname
        newUser.last_name = lname
        newUser.is_active = False
        newUser.save()

        # Email
        subject = 'Welcome to Django Authentication System'
        message = 'Hello ' + email + '!! \n\n' + 'Welcome to Authentication system made using Django.\nThank you for using. \n\nRegards, \nAshish Shimpi.'

        From = 'localhost'
        to_list = [email]
        send_mail(subject, message, From, to_list, fail_silently=True)


        try:
            current_site = get_current_site(request)
            subject = 'Activation link'
            context = {
                'name': newUser.first_name,
                'domain': current_site.domain,
                'uid' : urlsafe_base64_encode(force_bytes(newUser.pk)),
                'token' : generate_token.make_token(newUser)
            }
            
            message = render_to_string('activate.html',context, request)
    
            email = EmailMessage(
                subject,
                message,
                From,
                to_list,
            )
            email.send()
            
        except:
            messages.success(request,' The token code is broken')
            return redirect('home')
        messages.success(request,' The new user has been created')
        return redirect('signin')

    return render(request, "signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password= password)

        if user is not None:
            login(request, user)
            context = {
                "fname" : user.first_name
            }   
            
            return render(request, 'home.html',context)

        else:
            messages.error(request, 'User unknown. Please Sign Up')
            return redirect("home")


    return render(request,"signin.html")


def signout(request):
    logout(request)
    messages.success(request, 'User successfully logged out')
    return redirect("home")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request,'You are logged in using Activation link')
        context = {
                "fname" : user.first_name
            }    
        return render(request, 'home.html',context)

    else:
        return render(request, 'activation_failed.html')
