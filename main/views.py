from django.shortcuts import render,redirect
from .forms import PreviewForm, GraderForm
from preview.views import isTiny
from django.urls import reverse

def index(request):
    return redirect('login')

def home(request):
    return render(request, 'main/pages/home.html')

def blog(request):
    return render(request, 'main/pages/blog.html')

def upload(request):
    preview = PreviewForm(request.POST, request.FILES)

    if preview.is_valid():
        preview = preview.save()

        if isTiny(preview.form_image):
            return redirect(reverse('preview', kwargs={'preview_id': preview.id}))