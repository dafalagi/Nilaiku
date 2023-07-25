from django.shortcuts import render
from django.contrib.auth import logout as auth_logout
from grader.utils import Utils
from .models import User

# Create your views here.
def login(request):
    return render(request, 'main/pages/login.html')

def logout(request):
    user = User.objects.get(email=request.user.email)

    utils = Utils()
    if utils.deleteMedia(user.id):
        auth_logout(request)

        return render(request, 'main/pages/login.html')