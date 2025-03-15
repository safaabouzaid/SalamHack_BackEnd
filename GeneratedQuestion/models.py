from django.db import models

# Create your models here.
class GenerateQuestion(models.Model):
    job_field = models.CharField(max_length=255)
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Questions for {self.job_field}"
    

