from django.shortcuts import render
from django.contrib.auth import logout as auth_logout

# Create your views here.
def login(request):
    return render(request, 'main/pages/login.html')

def logout(request):
    auth_logout(request)
    return render(request, 'main/pages/login.html')