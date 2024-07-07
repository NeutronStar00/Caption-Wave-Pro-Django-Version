from django.urls import path
from . import views

urlpatterns = [
    path('process-video/', views.process_video, name='process_video'),
]
