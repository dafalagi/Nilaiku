from django.shortcuts import render, redirect, reverse
from .keyUtils import keyUtils
from .answerUtils import answerUtils
from .modelUtils import modelUtils
from .utils import Utils 
from .forms import UploadForm, KeyForm
from .models import Image, AnswerKey, GradeDetail
import grader.models as models
import json

# Create your views here.
def upload(request):
    upload = UploadForm(request.POST, request.FILES)

    if upload.is_valid():
        upload = upload.save()

        if (upload.form_type == 'key'):    
            key = KeyForm(request.POST)

            if key.is_valid():
                key = key.save(commit=False)
                key.image = upload
                key.save()
        elif (upload.form_type == 'answer'):
            answer = AnswerForm(request.POST)

            if answer.is_valid():
                answer.save()

        utils = Utils()
        if utils.isTiny(upload.form_image):
            return redirect(reverse('grading', kwargs={'img_id': upload.id}))

def grading(request, img_id):
    img = Images.objects.get(id=img_id)
    path = img.form_image
    form_type = img.form_type

    utils = Utils()    
    warped = utils.warping(path)

    if updateWarped(img_id, warped):
        if form_type == 'key':
            ku = keyUtils()
            path, key = ku.keyType(img_id)

            updateResult(img_id, path)
            updateKey(img_id, key)
        elif form_type == 'answer':
            au = answerUtils()
            path, correct, wrong, score = au.answerType(img_id)

            updateResult(img_id, path)
    
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