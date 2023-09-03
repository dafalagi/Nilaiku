from django.shortcuts import render,redirect
from django.db.models import Count
from grader.models import GradeDetail

def index(request):
    return redirect('login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    classes = []
    all_classes = (GradeDetail.objects
            .values('classes')
            .annotate(dcount=Count('classes'))
            .order_by('classes')
        )
    
    for class_ in all_classes:
        classes.append(class_['classes'])
    
    return render(request, 'main/pages/home.html', {
        'classes': classes
    })

def load_students(request):
    class_ = request.GET.get('classes')
    students = GradeDetail.objects.filter(classes=class_).order_by('name')

    return render(request, 'main/components/name_select.html', {
        'students': students
    })