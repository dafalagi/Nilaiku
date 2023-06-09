from .models import AnswerKey, Image
from .utils import Utils
from .forms import UploadForm, KeyForm, AnswerForm
from user.models import User

class modelUtils:
    def saveKey(self, img_id, answer_key):
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

    def upload(self, request):
        upload = UploadForm(request.POST, request.FILES)

        if upload.is_valid():
            upload = upload.save(commit=False)
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
                    answer.save()

                    result = {
                        'img_id': upload.id,
                        'answer_id': answer.id
                    }

            utils = Utils()
            if utils.isTiny(upload.form_image):

                return result