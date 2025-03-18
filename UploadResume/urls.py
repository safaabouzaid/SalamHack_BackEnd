from django.urls import path
from .views import ResumeUploadView

urlpatterns = [
    path('upload-resume/', ResumeUploadView.as_view(), name='upload-resume'),


]