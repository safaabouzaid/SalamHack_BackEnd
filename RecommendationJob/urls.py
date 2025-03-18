from django.urls import path
from .views import JobRecommendationView

urlpatterns = [
    path('recommendations/', JobRecommendationView.as_view(), name='job-recommendations'),
]
