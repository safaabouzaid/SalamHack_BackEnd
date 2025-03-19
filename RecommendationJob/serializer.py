from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    experience_required = serializers.CharField(allow_blank=True, required=False)
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'required_skills', 'experience_required', 'location']
