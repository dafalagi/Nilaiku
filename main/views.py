from django.shortcuts import render,redirect
from django.db.models import Count
from grader.models import GradeDetail, Course, Teacher, TeacherCourse

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
    
    courses = Course.objects.all()

    if request.session.get('classes') is not None:
        students = GradeDetail.objects.filter(classes=request.session.get('classes'))
        context = {
            'classes': classes,
            'courses': courses,
            'students': students
        }
    else:
        context = {
            'classes': classes,
            'courses': courses
        }
    
    return render(request, 'main/pages/home.html', {
        'context': context,
    })

def load_teachers(request):
    if not request.user.is_authenticated:
        return redirect('login')

    course = request.GET.get('course')
    teacher_courses = TeacherCourse.objects.filter(course=course)

    teachers = []
    for teacher_course in teacher_courses:
        teacher = Teacher.objects.get(id=teacher_course.teacher_id)
        teachers.append(teacher)

    return render(request, 'main/components/load-teachers.html', {
        'teachers': teachers
    })

def load_students(request):
    if not request.user.is_authenticated:
        return redirect('login')

    classes = request.GET.get('classes')
    students = GradeDetail.objects.filter(classes=classes)
    context = {
        'students': students
    }

    return render(request, 'main/components/load-students.html', {
        'context': context
    })