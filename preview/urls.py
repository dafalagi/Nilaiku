from django.urls import path
from . import views

urlpatterns = [
    path('<str:preview_id>', views.index, name='preview'),
]