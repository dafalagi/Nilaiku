from django.shortcuts import render, redirect
from .models import Preview
from .forms import PreviewForm, GraderForm
from django.urls import reverse
from .utils import Utils

# Create your views here.
def updateWarped(preview_id, warped_image):
    preview = Preview.objects.get(id=preview_id)
    preview.warped_image = warped_image
    preview.save()

    return True

def upload(request):
    preview = PreviewForm(request.POST, request.FILES)

    if preview.is_valid():
        preview = preview.save()

        if (preview.form_type == 'key'):    
            grader = GraderForm(request.POST)

            if grader.is_valid():
                grader = grader.save(commit=False)
                grader.preview = preview
                grader.save()

        utils = Utils()
        if utils.isTiny(preview.form_image):
            return redirect(reverse('preview', kwargs={'preview_id': preview.id}))

def preview(request, preview_id):
    preview = Preview.objects.get(id=preview_id)
    original = preview.form_image

    utils = Utils()    
    warped = utils.warping(original)

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