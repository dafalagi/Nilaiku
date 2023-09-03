from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from .keyUtils import KeyUtils
from .answerUtils import AnswerUtils
from .modelUtils import ModelUtils
from .utils import Utils 
from .models import Image, AnswerKey, GradeDetail, GradeSummary
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
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect('/home/#submitForm')

            utils.uploadToDOSpaces(path)
            modelUtils.updateResult(img.id, path)
            modelUtils.storeKey(img.id, key)
        elif form_type == 'answer':
            au = AnswerUtils()
            path, correct, wrong, score = au.answerType(img.id, request.user.email)
            if type(path) == bool:
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect('/home/#submitForm')

            keyImg, key = au.answerKey(request.user.email)
            answerKey = AnswerKey.objects.get(image_id=keyImg)

            utils.uploadToDOSpaces(path)
            modelUtils.updateResult(img.id, path)
            modelUtils.storeSummary(score, answerKey.id, upload['grade_detail_id'])

        img = Image.objects.get(id=img.id)

        if form_type == 'key':
            result = {
                'img': img.result_image,
                'form_type': form_type
            }
        elif form_type == 'answer':
            student = GradeDetail.objects.get(id=upload['grade_detail_id'])
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
        answerKey = AnswerKey.objects.get(id=request.POST['key_id'])
        summaries = GradeSummary.objects.filter(answer_key_id=answerKey)

        utils = Utils()
        if utils.writeExcel(summaries, request.user.email):
            response = utils.writeExcel(summaries, request.user.email)

            return response

    if User.objects.filter(email=request.user.email).exists():
        user = User.objects.get(email=request.user.email)
        keyImgs = Image.objects.filter(user=user, form_type='key')

        for keyImg in keyImgs:
            if AnswerKey.objects.filter(image_id=keyImg).exists():
                key = AnswerKey.objects.get(image_id=keyImg)
                summaries = (GradeSummary.objects
                    .values('answer_key_id')
                    .annotate(dcount=Count('answer_key_id'))
                    .order_by()
                )

        keys = []
        for summary in summaries:
            keys.append(AnswerKey.objects.get(id=summary['answer_key_id']))

        return render(request, 'main/pages/summary.html', {
            'keys': keys
        })
    else:
        return render(request, 'main/pages/summary.html')