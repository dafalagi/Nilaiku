from .models import Grader
import numpy as np
import cv2

class Utils:
    def imgFeatures(self, preview_id):
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

    def preprocessing(self, path):
        img = cv2.imread(path)

        imgWarpedGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgWarpedBlur = cv2.GaussianBlur(imgWarpedGray, (5, 5), 0)
        imgThre = cv2.adaptiveThreshold(imgWarpedBlur, 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,19,2)

        return imgThre

    def find_questions(self, cnts, image):
        questions = []
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            if (w >= 15 and h >= 15) and (w <= 50 and h <= 50) and ar >= 0.7 and ar <= 1.3:
                box = [(x//5)*5, y]
                questions.append([c, box])

        return questions

    def find_ques_cnts(self, questions, width):
        questions = sorted(questions, key=lambda q: q[1][1])
        questionCnts = []

        for i in np.arange(0, len(questions), width):
            q = list(questions[i: i+width])
            q = sorted(q, key=lambda k: k[1][0])
            for o in q:
                questionCnts.append(o[0])

        return questionCnts

    def convert_ques_no(self, q, rows_cnt, cols_cnt, hori_to_vert=True):
        if hori_to_vert:
            row = q // cols_cnt
            col = q % cols_cnt
            return col * rows_cnt + row
        col = q // rows_cnt
        row = q % rows_cnt
        
        return row * cols_cnt + col
