from .models import AnswerKey, Image, GradeSummary, GradeDetail
from .utils import Utils
from .forms import UploadForm, KeyForm, AnswerForm
from user.models import User

class ModelUtils:
    def storeKey(self, img_id, answer_key):
        store = AnswerKey()
        store.image_id = img_id
        store.answer_key = answer_key
        store.save()

        return True

    def updateResult(self, img_id, result):
        update = Image.objects.get(id=img_id)
        update.result_image = result
        update.save()

        return True

    def updateWarped(self, img_id, warped_image):
        update = Image.objects.get(id=img_id)
        update.warped_image = warped_image
        update.save()

        return True

    def storeUser(self, email):
        store = User()
        store.email = email
        store.save()

        return store

    def storeSummary(self, score, answer_key_id, grade_detail_id):
        store = GradeSummary()
        store.score = score
        store.answer_key_id = answer_key_id
        store.grade_detail_id = grade_detail_id
        store.save()

        return True

    def upload(self, request):
        upload = UploadForm(request.POST, request.FILES)

        if upload.is_valid():
            upload = upload.save(commit=False)
            
            if User.objects.filter(email=request.user.email).exists():
                upload.user = User.objects.get(email=request.user.email)
            else:
                upload.user = self.storeUser(request.user.email)

            upload.save()

            if (upload.form_type == 'key'):    
                key = KeyForm(request.POST)

                if key.is_valid():
                    key = key.save(commit=False)
                    key.image = upload
                    key.save()

                    result = {
                        'img_id': upload.id
                    }
            elif (upload.form_type == 'answer'):
                answer = AnswerForm(request.POST)

                if answer.is_valid():
                    if GradeDetail.objects.filter(name=answer.cleaned_data['name'], 
                    classes=answer.cleaned_data['classes']).exists():
                        answer = GradeDetail.objects.get(name=answer.cleaned_data['name'], 
                        classes=answer.cleaned_data['classes'])
                    else:
                        answer = answer.save()

                    result = {
                        'img_id': upload.id,
                        'grade_detail_id': answer.id
                    }

            utils = Utils()
            if utils.isTiny(upload.form_image):

                return result