from django.db import models
from preview.models import Preview

# Create your models here.
class Grader(models.Model):
    # user_id = models.CharField(
    #     max_length=100,
    #     foreign_key=True,
    #     on_delete=models.CASCADE,
    #     on_update=models.CASCADE,
    #     )
    preview = models.ForeignKey(
        Preview, 
        on_delete=models.CASCADE,
        )
    answer_key = models.JSONField(blank=True, null=True)
    height = models.IntegerField()
    choices = models.IntegerField()
    max_q = models.IntegerField()
    max_mark = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)