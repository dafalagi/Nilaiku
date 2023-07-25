from django.urls import path
from . import views

urlpatterns = [
    path('', views.grade, name='grade'),
    path('summary/', views.gradeSummary, name='summary')
]