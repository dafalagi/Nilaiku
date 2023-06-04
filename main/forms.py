from django import forms
from preview.models import Preview
from grader.models import Grader

class PreviewForm(forms.ModelForm):
    class Meta:
        model = Preview
        fields = ["form_type", "form_image"]

class GraderForm(forms.ModelForm):
    class Meta:
        model = Grader
        fields = ["height", "choices", "max_q", "max_mark"]