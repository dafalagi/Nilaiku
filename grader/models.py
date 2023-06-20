from django.db import models
from user.models import User

# Create your models here.
class Image(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        )
    form_type = models.CharField(max_length=100)
    form_image = models.ImageField(upload_to='images/')
    warped_image = models.ImageField(upload_to='images/', null=True)
    result_image = models.ImageField(upload_to='images/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ImgFeatures(models.Model):
    image = models.ForeignKey(
        Image, 
        on_delete=models.CASCADE,
        )
    height = models.IntegerField()
    choices = models.IntegerField()
    max_q = models.IntegerField()
    max_mark = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AnswerKey(models.Model):
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        )
    answer_key = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GradeDetail(models.Model):
    name = models.CharField(max_length=255)
    classes = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GradeSummary(models.Model):
    answer_key = models.ForeignKey(
        AnswerKey, 
        on_delete=models.CASCADE,
        )
    grade_detail = models.ForeignKey(
        GradeDetail, 
        on_delete=models.CASCADE,
        )
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)