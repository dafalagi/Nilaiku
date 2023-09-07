from .models import AnswerKey, Image, GradeSummary, GradeDetail, TeacherCourse, Exam
from .utils import Utils
from .forms import UploadForm
from user.models import User

class ModelUtils:
    def storeExam(self, user_id, teacher_course_id, classes, date):
        store = Exam()
        store.user_id = user_id
        store.teacher_course_id = teacher_course_id
        store.classes = classes
        store.date = date
        store.save()

        return store

    def storeKey(self, img_id, answer_key):
        store = AnswerKey()
        store.image_id = img_id
        store.answer_key = answer_key
        store.save()

        return store

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

    def storeSummary(self, score, answer_key_id, grade_detail_id, exam_id):
        if GradeSummary.objects.filter(answer_key_id=answer_key_id, grade_detail_id=grade_detail_id).exists():
            update = GradeSummary.objects.get(answer_key_id=answer_key_id, grade_detail_id=grade_detail_id)
            update.score = score
            update.save()
        else:
            store = GradeSummary()
            store.score = score
            store.answer_key_id = answer_key_id
            store.grade_detail_id = grade_detail_id
            store.exam_id = exam_id

            store.save()

        return True

    def upload(self, request):
        upload = UploadForm(request.POST, request.FILES)

        if upload.is_valid():
            utils = Utils()
            imgPath = utils.storeImage(request)
            
            upload = upload.save(commit=False)
            
            if User.objects.filter(email=request.user.email).exists():
                upload.user = User.objects.get(email=request.user.email)
            else:
                upload.user = self.storeUser(request.user.email)

            upload.save()

            result = utils.storeForm(request, upload)
            if (upload.form_type == 'key'):
                teacher_course = TeacherCourse.objects.get(teacher=request.POST['teacher'], course=request.POST['course'])
                
                if not Exam.objects.filter(user_id=request.user.id, teacher_course_id=teacher_course.id, classes=request.POST['classes'], 
                date=request.POST['date']).exists():
                    user = User.objects.get(email=request.user.email)
                    exam = self.storeExam(user.id, teacher_course.id, request.POST['classes'], request.POST['date'])

                    request.session['exam_id'] = exam.id
            elif (upload.form_type == 'answer'):
                if request.session.get('classes') is None:
                    request.session['classes'] = request.POST['classes']

                    exam = Exam.objects.get(id=request.session.get('exam_id'))
                    exam.classes = request.POST['classes']
                    exam.save()
                else:
                    if request.session.get('classes') != request.POST['classes']:
                        request.session['classes'] = request.POST['classes']
                        exam = Exam.objects.get(id=request.session.get('exam_id'))

                        if not Exam.objects.filter(user_id=exam.user_id, teacher_course_id=exam.teacher_course_id,
                        classes=request.POST['classes'], date=exam.date).exists():
                            store = self.storeExam(exam.user_id, exam.teacher_course_id, request.POST['classes'], exam.date)
                            request.session['exam_id'] = store.id
                        else:
                            exam = Exam.objects.get(user_id=exam.user_id, teacher_course_id=exam.teacher_course_id,
                            classes=request.POST['classes'], date=exam.date)
                            request.session['exam_id'] = exam.id

            if utils.isTiny(imgPath):

                return result