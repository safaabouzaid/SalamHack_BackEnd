from django.urls import path
from .views import ConvertResumeAPIView

urlpatterns = [
    path('convert-resume/', ConvertResumeAPIView.as_view(), name='convert_resume'),

]