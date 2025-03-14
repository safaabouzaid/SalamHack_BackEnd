from django.urls import path
from .views import ResumeEvaluationView

urlpatterns = [
    path('evaluation-resume/<int:resume_id>/', ResumeEvaluationView.as_view(), name='evaluation_resume'),

]