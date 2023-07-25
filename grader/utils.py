from django.conf import settings
from .models import ImgFeatures, Image
from imutils.perspective import four_point_transform
from decouple import config
import datetime
import numpy as np
import tinify, cv2, os

class Utils:
    def imgFeatures(self, img_id):
        img = ImgFeatures.objects.get(image_id=img_id)

        max_mark = img.max_mark
        max_q = img.max_q
        choices = img.choices
        height = img.height
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

    def ogPreprocessing(self, file):
        img = cv2.imread('media/'+file.name)

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
        imgCanny = cv2.Canny(imgBlur, 20, 50)

        return imgCanny

    def roiPreprocessing(self, path):
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

    def isTiny(self, file):
        tinify.key = config('TINIFY_KEY')

        size = os.path.getsize('media/'+file.name)

        if size > 5000000:
            source = tinify.from_file('media/'+file.name)
            source.to_file('media/'+file.name)

        return True

    def warping(self, file):
        img = cv2.imread('media/'+file.name)
        preprocessed = self.ogPreprocessing(file)

        contours, hierarchy = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rectCont = self.rectContour(contours)
        biggestContour = self.getCornerPoints(rectCont[0])

        if biggestContour.size != 0:
            imgOutput = four_point_transform(img, biggestContour.reshape(4, 2))

            basename = os.path.basename(file.name)
            cv2.imwrite('media/images/warped'+basename, imgOutput)
            warped = 'images/warped'+basename

            return warped
            
    def rectContour(self, contours):
        rectCon = []
        maxArea = 0

        for i in contours:
            area = cv2.contourArea(i)
            if area > 50:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02*peri, True)
                if len(approx) == 4:
                    rectCon.append(i)

        rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)

        return rectCon

    def getCornerPoints(self, cont):
        peri = cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, 0.02*peri, True)

        return approx

    def deleteMedia(self, user_id):
        images = Image.objects.filter(user_id=user_id)
        media_dir = settings.MEDIA_ROOT

        for img in images:
            if img.form_image:
                path = os.path.join(media_dir, str(img.form_image))
                if os.path.exists(path):
                    os.remove()
            if img.result_image:
                path = os.path.join(media_dir, str(img.result_image))
                if os.path.exists(path):
                    os.remove()
            if img.warped_image:
                path = os.path.join(media_dir, str(img.warped_image))
                if os.path.exists(path):
                    os.remove()

        return True