from django.shortcuts import render
from decouple import config
import tinify, cv2
from .models import Preview

# Create your views here.

def isTiny(file):
    tinify.key = config('TINIFY_KEY')

    img = cv2.imread(file.name)
    dimensions = img.shape
    height = dimensions[0]
    width = dimensions[1]

    if width > 2000 or height > 2000:
        source = tinify.from_file(file.name)
        source.to_file(file.name)

    return True

def index(request, preview_id):
    preview = Preview.objects.get(id=preview_id)
    img = preview.form_image

    return render(request, 'main/pages/preview.html')