from django.urls import path
from .views import ResumeUploadView

urlpatterns = [
    path('upload-resume/<int:user_id>/', ResumeUploadView.as_view(), name='upload-resume'),


]