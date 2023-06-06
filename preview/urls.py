from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('<int:preview_id>', views.preview, name='preview'),
]