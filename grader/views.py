from django.shortcuts import render
from preview.models import Preview
from grader.models import Grader
from .keyUtils import keyUtils
from .answerUtils import answerUtils
import json

# Create your views here.
def updateKey(preview_id, answer_key):
    grader = Grader.objects.get(preview_id=preview_id)
    grader.answer_key = answer_key
    grader.save()

    return True

def updateResult(preview_id, result):
    preview = Preview.objects.get(id=preview_id)
    preview.result_image = result
    preview.save()

    return True

def grade(request):
    preview_id = request.POST.get('preview_id')
    form_type = request.POST.get('form_type')

    ku = keyUtils()
    au = answerUtils()

    if form_type == 'key':
        path, key = ku.keyType(preview_id)
        updateResult(preview_id, path)
        updateKey(preview_id, key)

        grader = Grader.objects.get(preview_id=preview_id)
    elif form_type == 'answer':
        path, correct, wrong, score = au.answerType(preview_id)
        updateResult(preview_id, path)

        grader = Grader.objects.get(preview_id=9)

    preview = Preview.objects.get(id=preview_id)
    key = json.loads(grader.answer_key)

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