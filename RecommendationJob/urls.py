from django.urls import path
from .views import JobRecommendationView

urlpatterns = [
    path('recommendations/<int:user_id>/', JobRecommendationView.as_view(), name='job-recommendations'),
]
