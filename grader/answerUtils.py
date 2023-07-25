from .models import Image, AnswerKey
from .utils import Utils
from user.models import User
import numpy as np
import cv2, json, os

class AnswerUtils:
    def answerType(self, img_id, email):
        img = Image.objects.get(id=img_id)
        path = 'media/'+img.warped_image.name

        keyImg, key = self.answerKey(email)

        utils = Utils()
        features = utils.imgFeatures(keyImg.id)
        preprocessed = utils.roiPreprocessing(path)

        result, correct, wrong = self.answerProcess(path, features, preprocessed, key)
        score = self.scoring(correct, wrong, features['max_mark'])

        basename = os.path.basename(img.form_image.name)
        cv2.imwrite('media/images/result'+basename, result)
        path = 'images/result'+basename

        return path, correct, wrong, score

    def answerKey(self, email):
        user = User.objects.get(email=email)
        keyImg = Image.objects.filter(user=user, form_type='key').order_by('-id')[0]

        answer = AnswerKey.objects.get(image_id=keyImg.id)
        key = json.loads(answer.answer_key)

        return keyImg, key

    def answerProcess(self, path, features, preprocessed, key):
        img = cv2.imread(path)
        correct = 0
        wrong = 0
        utils = Utils()

        contours, hierarchy = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        questions = utils.find_questions(contours, img)
        questionCnts = utils.find_ques_cnts(questions, features['width'])

        for (q, i) in enumerate(np.arange(0, len(questionCnts), features['choices'])):
            old_question_no = utils.convert_ques_no(q, features['height'], features['batch'])

            cnts = questionCnts[i:i+features['choices']]
            bubbled = [0, 0, 0]

            for (j, c) in enumerate(cnts):
                mask = np.zeros(preprocessed.shape, dtype='uint8')
                cv2.drawContours(mask, [c], -1, 255, -1)

                mask = cv2.bitwise_and(preprocessed, preprocessed, mask=mask)
                total = cv2.countNonZero(mask)

                if old_question_no >= features['max_mark']:
                    pass
                else:
                    if bubbled[1] == 0:
                        bubbled = (old_question_no, total, j)
                    elif bubbled[1] < total:
                        bubbled = (old_question_no, total, j)
            color = (0, 0, 255)
            if old_question_no >= features['max_mark']:
                pass
            else:
                k = key[str(old_question_no)]

                if k == bubbled[2]:
                    color = (0, 255, 0)
                    cv2.drawContours(img, [cnts[k]], -1, color, 2)
                    correct += 1
                elif k != bubbled[2]:
                    cv2.drawContours(img, [cnts[k]], -1, color, 2)
                    wrong += 1

        return img, correct, wrong

    def scoring(self, correct, wrong, max_mark):
        score = correct/max_mark*100

        return score