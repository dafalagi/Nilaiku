from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from .keyUtils import KeyUtils
from .answerUtils import AnswerUtils
from .modelUtils import ModelUtils
from .utils import Utils 
from .models import Image, AnswerKey, GradeDetail, GradeSummary, Exam, Teacher, Course, TeacherCourse
from user.models import User
import grader.models as models
import json, os, mimetypes

# Create your views here.
def grade(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    modelUtils = ModelUtils()
    upload = modelUtils.upload(request)

    img = Image.objects.get(id=upload['img_id'])
    path = img.form_image
    form_type = img.form_type

    utils = Utils()
    warped = utils.warping(path)

    if modelUtils.updateWarped(img.id, warped):
        if form_type == 'key':
            ku = KeyUtils()
            path, key = ku.keyType(img.id)
            if type(path) == bool:
                messages.error(request, 'Terjadi kesalahan! Silahkan unggah kembali foto LJK anda.')
                return redirect('/home/#submitForm')

            utils.uploadToDOSpaces(path)
            modelUtils.updateResult(img.id, path)

            answer_key = modelUtils.storeKey(img.id, key)
            request.session['answer_key_id'] = answer_key.id
        elif form_type == 'answer':
            if request.session.get('answer_key_id') is None:
                messages.error(request, 'Kunci jawaban tidak ditemukan! Silahkan unggah kunci jawaban terlebih dahulu.')
                return redirect('/home/#submitForm')

            au = AnswerUtils()
            path, correct, wrong, score = au.answerType(img.id, request.session.get('answer_key_id'))
            if type(path) == bool:
                messages.error(request, 'Terjadi kesalahan! Silahkan unggah kembali foto LJK anda.')
                return redirect('/home/#submitForm')

            utils.uploadToDOSpaces(path)
            modelUtils.updateResult(img.id, path)
            modelUtils.storeSummary(score, request.session.get('answer_key_id'), upload['grade_detail_id'], request.session.get('exam_id'))

        img = Image.objects.get(id=img.id)

        if form_type == 'key':
            user = User.objects.get(email=request.user.email)
            exam = Exam.objects.filter(user_id=user.id).order_by('-id')[0]
            teacher_course = TeacherCourse.objects.get(id=exam.teacher_course_id)
            teacher = Teacher.objects.get(id=teacher_course.teacher_id)
            course = Course.objects.get(id=teacher_course.course_id)
            
            result = {
                'img': img.result_image,
                'teacher': teacher.name,
                'course': course.name,
                'classes': exam.classes,
                'date': exam.date,
                'form_type': form_type
            }
        elif form_type == 'answer':
            student = GradeDetail.objects.get(id=upload['grade_detail_id'])
            request.session['student_id'] = student.id + 1

            result = {
                'name': student.name,
                'classes': student.classes,
                'img': img.result_image,
                'correct': correct,
                'wrong': wrong,
                'score': "%.1f" % score,
                'form_type': form_type
            }
            
        return render(request, 'main/pages/grade.html', {
            'result': result
        })

def gradeSummary(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        utils = Utils()
        if utils.writeExcel(request.POST['exam_id']):
            response = utils.writeExcel(request.POST['exam_id'])

            return response

    if User.objects.filter(email=request.user.email).exists():
        user = User.objects.get(email=request.user.email)
        exams = Exam.objects.filter(user_id=user.id)

        summaries = []
        for exam in exams:
            if exam.classes == 'False':
                exam.delete()
            else:
                teacher_course = TeacherCourse.objects.get(id=exam.teacher_course_id)
                teacher = Teacher.objects.get(id=teacher_course.teacher_id)
                course = Course.objects.get(id=teacher_course.course_id)

                summary = {
                    'teacher': teacher.name,
                    'course': course.name,
                    'classes': exam.classes,
                    'date': exam.date,
                    'exam_id': exam.id,
                }

                summaries.append(summary)

        return render(request, 'main/pages/summary.html', {
            'summaries': summaries
        })
    else:
        return render(request, 'main/pages/summary.html')