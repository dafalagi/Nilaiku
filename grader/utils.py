from django.conf import settings
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from imutils.perspective import four_point_transform
from decouple import config
from .models import ImgFeatures, Image, GradeDetail
from .forms import KeyForm, AnswerForm
import numpy as np
import tinify, cv2, os, xlsxwriter, io, boto3

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

    def convert_ques_no(self, q, rows_cnt, cols_cnt):
        row = q // cols_cnt
        col = q % cols_cnt
        
        return col * rows_cnt + row

    def isTiny(self, file):
        tinify.key = config('TINIFY_KEY')

        size = os.path.getsize('media/'+file)

        if size > 4000000:
            source = tinify.from_file('media/'+file)
            source.to_file('media/'+file)

        return True

    def warping(self, file):
        img = cv2.imread('media/'+file.name)

        if (img.shape[1] > 2000 or img.shape[0] > 4000):
            scale_percent = 43
            widthImg = int(img.shape[1] * scale_percent / 100)
            heightImg = int(img.shape[0] * scale_percent / 100)
            dim = (widthImg, heightImg)

            img = cv2.resize(img, dim)
            cv2.imwrite('media/'+file.name, img)
            
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

    def deleteImage(self, user_id):
        images = Image.objects.filter(user_id=user_id)
        media_dir = os.path.join(settings.BASE_DIR, 'media/')

        for img in images:
            if img.form_image:
                path = os.path.join(media_dir, str(img.form_image))
                if os.path.exists(path):
                    os.remove(path)
            if img.result_image:
                path = os.path.join(media_dir, str(img.result_image))
                if os.path.exists(path):
                    os.remove(path)
            if img.warped_image:
                path = os.path.join(media_dir, str(img.warped_image))
                if os.path.exists(path):
                    os.remove(path)

        return True

    def storeImage(self, request):
        if settings.USE_SPACES == True:
            filename = request.FILES['form_image'].name
            base_path = os.path.join(settings.BASE_DIR, 'media/images/')

            if os.path.exists(base_path) == False:
                os.makedirs(base_path)

            path = os.path.join(base_path, filename)
            fout = open(path, 'wb+')

            content = ContentFile(request.FILES['form_image'].read())

            for chunk in content.chunks():
                fout.write(chunk)
            fout.close()

            imgPath = 'images/'+filename
        else:
            imgPath = upload.form_image.name

        return imgPath

    def storeForm(self, request, upload):
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
        
        return result

    def writeExcel(self, summaries, email):
        date = summaries[0].created_at.strftime("%d/%m/%Y")
        filename = email+'_'+date+'.xlsx'

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
        })
        content_format = workbook.add_format({
            'border': 1,
        })
        no_format = workbook.add_format({
            'border': 1,
            'align': 'center',
        })
        bold = workbook.add_format({'bold': True})

        worksheet.write(1, 1, 'Tanggal Penilaian:', bold)
        worksheet.write(1, 2, date)
        worksheet.write(3, 0, 'No', header_format)
        worksheet.write(3, 1, 'Nama', header_format)
        worksheet.write(3, 2, 'Kelas', header_format)
        worksheet.write(3, 3, 'Nilai', header_format)

        row = 4
        col = 0
        no = 1

        for summary in summaries:
            gradeDetail = GradeDetail.objects.get(id=summary.grade_detail_id)

            worksheet.write(row, col, no, no_format)
            worksheet.write(row, col+1, gradeDetail.name, content_format)
            worksheet.write(row, col+2, gradeDetail.classes, content_format)
            worksheet.write(row, col+3, summary.score, content_format)
            row += 1
            no += 1

        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=%s" % filename

        output.close()

        return response

    def connectToDOSpaces(self):
        session = boto3.session.Session()
        client = session.client(
            's3',
            region_name='sgp1',
            endpoint_url='https://sgp1.digitaloceanspaces.com',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')
        )

        return client

    def uploadToDOSpaces(self, file):
        client = self.connectToDOSpaces()

        with open('media/'+file, 'rb') as file_contents:
            client.put_object(
                Bucket='nilaikuspaces',
                Key='media/'+file,
                ACL='public-read',
                Body=file_contents
            )

        return True