from grader.models import Grader
from .utils import Utils
import cv2, numpy as np, json

class keyUtils:
    def imgFeatures(preview_id):
        grader = Grader.objects.get(preview_id=preview_id)

        max_mark = grader.max_mark
        max_q = grader.max_q
        choices = grader.choices
        height = grader.height
        batch = int(max_q/height)
        width = int((max_q*choices)/height)

        return {
            'max_mark': max_mark,
            'max_q': max_q,
            'choices': choices,
            'height': height,
            'batch': batch,
            'width': width
        }

    def preprocessing(path):
        img = cv2.imread(path)

        imgWarpedGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgWarpedBlur = cv2.GaussianBlur(imgWarpedGray, (5, 5), 0)
        imgThre = cv2.adaptiveThreshold(imgWarpedBlur, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,19,2)

        return imgThre

    def processKey(path, features, preprocessed):
        img = cv2.imread(path)
        key = []

        contours, hierarchy = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        questions = Utils.find_questions(contours, img)
        questionCnts = Utils.find_ques_cnts(questions, features['width'])

        for (q, i) in enumerate(np.arange(0, len(questionCnts), features['choices'])):
            old_question_no = Utils.convert_ques_no(q, features['height'], features['batch'])

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