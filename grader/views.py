from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from .keyUtils import KeyUtils
from .answerUtils import AnswerUtils
from .modelUtils import ModelUtils
from .utils import Utils 
from .models import Image, AnswerKey, GradeDetail, GradeSummary
from user.models import User
import grader.models as models
import json, os

# Create your views here.
def grade(request):
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

            modelUtils.updateResult(img.id, path)
            modelUtils.storeKey(img.id, key)
        elif form_type == 'answer':
            au = AnswerUtils()
            path, correct, wrong, score = au.answerType(img.id, request.user.email)

            keyImg, key = au.answerKey(request.user.email)
            answerKey = AnswerKey.objects.get(image_id=keyImg)

            modelUtils.updateResult(img.id, path)
            modelUtils.storeSummary(score, answerKey.id, upload['grade_detail_id'])

        img = Image.objects.get(id=img.id)

        if form_type == 'key':
            result = {
                'img': img.result_image,
                'key': key,
                'form_type': form_type
            }
        elif form_type == 'answer':
            result = {
                'img': img.result_image,
                'correct': correct,
                'wrong': wrong,
                'score': "%.1f" % score,
                'key': key,
                'form_type': form_type
            }
            
        return render(request, 'main/pages/grade.html', {
            'result': result
        })

def gradeSummary(request):
    if request.method == 'POST':
        answerKey = AnswerKey.objects.get(image_id=request.POST['key_id'])
        summaries = GradeSummary.objects.filter(answer_key_id=answerKey)

        utils = Utils()
        if utils.writeExcel(summaries, request.user.email):
            path = 'media/summaries/'+request.user.email+'_'+summaries[0].created_at.strftime("%d%m%Y")+'.xlsx'
            filename = request.user.email+'_'+summaries[0].created_at.strftime("%d%m%Y")+'.xlsx'

            if os.path.exists(path):
                content = open(path, 'r')
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=%s' % filename

                return response

    if User.objects.filter(email=request.user.email).exists():
        user = User.objects.get(email=request.user.email)
        keys = Image.objects.filter(user=user, form_type='key')

        return render(request, 'main/pages/summary.html', {
            'keys': keys
        })
    else:
        return render(request, 'main/pages/summary.html')