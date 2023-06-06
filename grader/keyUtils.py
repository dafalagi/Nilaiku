from .models import Preview
from .utils import Utils
import numpy as np
import cv2, json, os

class keyUtils:
    def keyType(self, preview_id):
        preview = Preview.objects.get(id=preview_id)
        path = 'media/'+preview.warped_image.name

        utils = Utils()
        features = utils.imgFeatures(preview_id)
        preprocessed = utils.preprocessing(path)

        result, key = self.keyProcess(path, features, preprocessed)

        basename = os.path.basename(preview.form_image.name)
        cv2.imwrite('media/images/result'+basename, result)
        path = 'images/result'+basename

        return path, key

    def keyProcess(self, path, features, preprocessed):
        img = cv2.imread(path)
        key = []
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
            color = (0, 255, 0)
            if old_question_no >= features['max_mark']:
                pass
            else:
                key.append([bubbled[0], bubbled[2]])
                cv2.drawContours(img, [cnts[bubbled[2]]], -1, color, 2)

        key = dict(key)
        key = json.dumps(key)

        return img, key