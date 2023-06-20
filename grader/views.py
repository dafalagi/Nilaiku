from django.shortcuts import render, redirect, reverse
from .keyUtils import keyUtils
from .answerUtils import answerUtils
from .modelUtils import modelUtils
from .utils import Utils 
from .models import Image, AnswerKey, GradeDetail
import grader.models as models
import json

# Create your views here.
def grade(request):
    upload = modelUtils.upload(request)

    img = Images.objects.get(id=upload['img_id'])
    path = img.form_image
    form_type = img.form_type

    utils = Utils()
    modelUtils = modelUtils()
    warped = utils.warping(path)

    if updateWarped(img_id, warped):
        if form_type == 'key':
            ku = keyUtils()
            path, key = ku.keyType(img_id)

            modelUtils.updateResult(img_id, path)
            modelUtils.updateKey(img_id, key)
        elif form_type == 'answer':
            au = answerUtils()
            path, correct, wrong, score = au.answerType(img_id)

            modelUtils.updateResult(img_id, path)
    
        answer = AnswerKey.objects.get(img_dir_id=img_id)
        img = Image.objects.get(id=img_id)
        key = json.loads(answer.answer_key)

        if form_type == 'key':
            result = {
                'img': preview.result_image,
                'key': key,
                'form_type': form_type
            }
        elif form_type == 'answer':
            result = {
                'img': preview.result_image,
                'correct': correct,
                'wrong': wrong,
                'score': "%.1f" % score,
                'key': key,
                'form_type': form_type
            }
            
        return render(request, 'main/pages/main-content.html', {
            'result': result
        })