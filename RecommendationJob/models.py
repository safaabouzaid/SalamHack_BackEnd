from django.db import models

# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length=255)  
    description = models.TextField()  
    required_skills = models.TextField()  
    experience_required = models.IntegerField(default=0, blank=True)  
    location = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return self.title
