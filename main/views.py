from django.shortcuts import render,redirect

def index(request):
    return redirect('login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'main/pages/home.html')