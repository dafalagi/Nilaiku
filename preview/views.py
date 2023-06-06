import tinify, cv2, os
from django.shortcuts import render, redirect
from decouple import config
from .models import Preview
from .forms import PreviewForm, GraderForm
from django.urls import reverse
from .utils import Utils
from imutils.perspective import four_point_transform

# Create your views here.

def updateWarped(preview_id, warped_image):
    preview = Preview.objects.get(id=preview_id)
    preview.warped_image = warped_image
    preview.save()

    return True

def isTiny(file):
    tinify.key = config('TINIFY_KEY')

    img = cv2.imread('media/'+file.name)
    dimensions = img.shape
    height = dimensions[0]
    width = dimensions[1]

    if width > 2000 or height > 2000:
        source = tinify.from_file('media/'+file.name)
        source.to_file('media/'+file.name)

    return True

def preprocessing(file):
    img = cv2.imread('media/'+file.name)

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
    imgCanny = cv2.Canny(imgBlur, 20, 50)

    return imgCanny

def warping(file):
    img = cv2.imread('media/'+file.name)
    preprocessed = preprocessing(file)

    contours, hierarchy = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rectCont = Utils.rectContour(contours)
    biggestContour = Utils.getCornerPoints(rectCont[0])

    if biggestContour.size != 0:
        imgOutput = four_point_transform(img, biggestContour.reshape(4, 2))

        basename = os.path.basename(file.name)
        cv2.imwrite('media/images/warped'+basename, imgOutput)
        warped = 'images/warped'+basename

        return warped

def upload(request):
    preview = PreviewForm(request.POST, request.FILES)
    grader = GraderForm(request.POST)

    if preview.is_valid() and grader.is_valid():
        preview = preview.save()

        grader = grader.save(commit=False)
        grader.preview = preview
        grader.save()

        if isTiny(preview.form_image):
            return redirect(reverse('preview', kwargs={'preview_id': preview.id}))

def preview(request, preview_id):
    preview = Preview.objects.get(id=preview_id)
    original = preview.form_image
    warped = warping(original)

    if updateWarped(preview_id, warped):
        preview = Preview.objects.get(id=preview_id)
        warped = preview.warped_image
        form_type = preview.form_type

        return render(request, 'main/pages/main-content.html', {
            'original': original,
            'warped': warped,
            'preview_id': preview_id,
            'form_type': form_type,
            'url': '/preview/'+str(preview_id)
        })