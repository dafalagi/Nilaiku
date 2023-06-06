from django.db import models

# Create your models here.
class Preview(models.Model):
    # user_id = models.CharField(
    #     max_length=100,
    #     foreign_key=True,
    #     on_delete=models.CASCADE,
    #     on_update=models.CASCADE,
    #     )
    form_type = models.CharField(max_length=100)
    form_image = models.ImageField(upload_to='images/')
    warped_image = models.ImageField(upload_to='images/', null=True)
    result_image = models.ImageField(upload_to='images/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)