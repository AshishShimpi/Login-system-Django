
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

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


        if cpassword != password:
            messages.error(request, 'Passwords must be same')

        if User.objects.filter(username = username):
            messages.error(request, 'Username already exists!. Please try different username')
        
        
        newUser = User.objects.create_user(username, email, password)
        newUser.first_name = fname
        newUser.last_name = lname

        newUser.save()

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
