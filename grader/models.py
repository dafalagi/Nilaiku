from django.db import models

# Create your models here.
class Grader(models.Model):
    email = models.EmailField(max_length=254)
    answer_key = models.CharField(
        max_length=254,
        null=True,
        )
    unoptimized_dir = models.CharField(
        max_length=254,
        null=True,
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)