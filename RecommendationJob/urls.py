from django.urls import path
from .views import JobRecommendationView,JobAPIView

urlpatterns = [
    path('recommendations/', JobRecommendationView.as_view(), name='job-recommendations'),
    path('jobs/', JobAPIView.as_view(), name='job-list-create'),

]
