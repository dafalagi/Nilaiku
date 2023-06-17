from .models import AnswerKey, Image

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