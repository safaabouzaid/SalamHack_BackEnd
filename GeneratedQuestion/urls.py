from django.urls import path
from .views import GenerateQuestionView

urlpatterns = [
    path('generate-questions/', GenerateQuestionView.as_view(), name='generate_questions'),
]