from django import forms
from grader.models import Grader

class GraderForm(forms.ModelForm):
    class Meta:
        model = Grader
        fields = "__all__"