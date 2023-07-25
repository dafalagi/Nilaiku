from django.shortcuts import render, redirect, reverse
from .keyUtils import KeyUtils
from .answerUtils import AnswerUtils
from .modelUtils import ModelUtils
from .utils import Utils 
from .models import Image, AnswerKey, GradeDetail
import grader.models as models
import json

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
            answerKey = AnswerKey.objects.get(image_id=keyImg.id)

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
    return render(request, 'main/pages/summary.html')