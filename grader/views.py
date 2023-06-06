from django.shortcuts import render
from preview.models import Preview
from grader.models import Grader
import json, os 
from .keyUtils import keyUtils as ku

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

def keyType(preview_id):
    preview = Preview.objects.get(id=preview_id)
    path = 'media/'+preview.warped_image.name

    features = ku.imgFeatures(preview_id)
    preprocessed = ku.preprocessing(path)
    result, key = ku.processKey(path, features, preprocessed)

    cv2.imwrite('media/images/result'+preview.form_image.name, result)
    basename = os.path.basename(preview.form_image.name)
    path = 'images/result'+basename

    updateResult(preview_id, path)
    updateKey(preview_id, key)

    return True

def grade(request):
    preview_id = request.POST.get('preview_id')
    form_type = request.POST.get('form_type')

    if form_type == 'key':
        keyType(preview_id)
    elif form_type == 'answer':
        typeAnswer(preview_id)

    preview = Preview.objects.get(id=preview_id)
    grader = Grader.objects.get(preview_id=preview_id)

    key = json.loads(grader.answer_key)

    return render(request, 'main/pages/main-content.html', {
        'result': preview.result_image,
        'key': key,
    })