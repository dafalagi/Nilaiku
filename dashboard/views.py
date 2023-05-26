from django.shortcuts import render, redirect
from grader.models import Grader
from .forms import GraderForm
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, 'admin/index.html')

def create(request):
    if request.method == 'POST':
        form = GraderForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']

            grader = Grader(title=title, body=body)
            grader.save()
            
            return redirect('data-tables')
        else:
            messages.info(request, 'Invalid Value')
            return redirect('create')
    else:
        return render(request, 'admin/pages/pages-create.html')

def update(request, id):
    grader = Grader.objects.get(id=id)
    if request.method == 'POST':
        form = GraderForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']

            grader.title = title
            grader.body = body
            grader.save()
            
            return redirect('data-tables')
        else:
            messages.info(request, 'Invalid Value')
            return redirect('update', id)
    else:
        return render(request, 'admin/pages/pages-update.html', {
            'grader': grader
        })

def delete(request, id):
    grader = Grader.objects.get(id=id)
    grader.delete()
    return redirect('data-tables')

def show(request, id):
    grader = Grader.objects.get(id=id)
    return render(request, 'admin/pages/pages-show.html', {
        'grader': grader
    })

def index(request):
    grader = Grader.objects.all()
    fields = Grader._meta.get_fields()
    return render(request, 'admin/tables/tables-data.html', {    
        'graders': grader,
        'fields': fields
    })