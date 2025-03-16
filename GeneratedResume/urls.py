from django.urls import path
from .views import ResumeAPIView,ResumeUploadView

urlpatterns = [
    path('generate-resume/', ResumeAPIView.as_view(), name='generate_resume'),
    path('upload-resume/<int:user_id>/', ResumeUploadView.as_view(), name='upload-resume'),


]