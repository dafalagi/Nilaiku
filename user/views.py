from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from grader.utils import Utils
from .models import User

# Create your views here.
def login(request):
    return render(request, 'main/pages/login.html')

def logout(request):
    if User.objects.filter(email=request.user.email).exists():
        user = User.objects.get(email=request.user.email)

        utils = Utils()
        if utils.deleteMedia(user.id):
            auth_logout(request)

            return redirect('login')

    else:
        auth_logout(request)

        return redirect('login')