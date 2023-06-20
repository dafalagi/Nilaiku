from django.shortcuts import render,redirect

def index(request):
    return redirect('login')

def home(request):
    if request.user.is_authenticated == False:
        return redirect('login')
    
    return render(request, 'main/pages/home.html')

def blog(request):
    return render(request, 'main/pages/blog.html')