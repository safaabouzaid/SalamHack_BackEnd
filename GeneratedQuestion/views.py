from django.shortcuts import render
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import GenerateQuestion
from .serializers import GenerateQuestionSerializer
import google.generativeai as genai
from .utils import extract_json 

def generate_questions(job_field):

    input_prompt = f'''
    You are an AI assistant. Provide exactly 5 technical interview questions related to "{job_field}" in JSON format.
    Strictly follow this format:
    {{
        "questions": [
            "Question 1?",
            "Question 2?",
            "Question 3?",
            "Question 4?",
            "Question 5?"
        ]
    }}
    '''

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt])

    if not response or not response.text.strip():
        return {"questions": ["No valid response received from the model"]}

    json_text = extract_json(response.text.strip())

    try:
        return json.loads(json_text) if json_text else {"questions": ["Invalid JSON format received from the model"]}
    except json.JSONDecodeError:
        return {"questions": ["Invalid JSON format received from the model"]}

class GenerateQuestionView(APIView):

    def post(self, request):
        job_field = request.data.get("job_field")
        if not job_field:
            return Response({"error": "job_field is required"}, status=status.HTTP_400_BAD_REQUEST)

        generated_questions = generate_questions(job_field)

        if "Invalid JSON format received from the model" in generated_questions["questions"]:
            return Response({"error": "Failed to generate valid questions"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        question_entry = GenerateQuestion.objects.create(
            job_field=job_field,
            questions=generated_questions["questions"]
        )
        serializer = GenerateQuestionSerializer(question_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)