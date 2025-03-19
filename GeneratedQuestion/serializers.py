from rest_framework import serializers
from .models import GenerateQuestion



class GenerateQuestionSerializer(serializers.ModelSerializer):
   class Meta:
      model = GenerateQuestion
      fields = ['job', 'questions']





