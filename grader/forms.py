from django import forms
from .models import Image, ImgFeatures, GradeDetail

class UploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["form_type", "form_image"]

class KeyForm(forms.ModelForm):
    class Meta:
        model = ImgFeatures
        fields = ["height", "choices", "max_q", "max_mark"]

class AnswerForm(forms.ModelForm):
    class Meta:
        model = GradeDetail
        fields = ["name", "score"]