from django.db import models
from RecommendationJob.models import Job 

# Create your models here.
class GenerateQuestion(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="questions")
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Questions for {self.job}"
    

