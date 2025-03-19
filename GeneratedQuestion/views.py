from django.shortcuts import render
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import GenerateQuestion
from RecommendationJob.models import Job
from .serializers import GenerateQuestionSerializer
import google.generativeai as genai
from .utils import extract_json

def generate_questions(title, required_skills, description):
    input_prompt = f'''
    You are an AI assistant specializing in job interview preparation. Generate exactly 5 multiple-choice questions (MCQs) 
    for a job interview based on the following job title, description, and required skills.
    
    The questions should:
    - Reflect real-world job interview scenarios.
    - Test problem-solving, debugging, and practical experience.
    - Include technical questions with real-world applications.
    - Contain at least one question that involves analyzing code.

    Job Title: {title}
    Job Description: {description}
    Required Skills: {required_skills}

    Each MCQ should have:
    - A question string.
    - Four options in an array, where each option is a string.
    - The correct answer as the index of the correct option (starting from 0).

    Strictly follow this format:
    {{
        "questions": [
            {{
                "question": "What is ...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0
            }},
            {{
                "question": "Which of the following ...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 2
            }}
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
        title = request.data.get("title")
        required_skills = request.data.get("required_skills")
        description = request.data.get("description")

        if not title or not required_skills or not description:
            return Response({"error": "title, required_skills, and description are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        job, created = Job.objects.get_or_create(
            title=title, 
            description=description, 
            required_skills=required_skills
        )
        
        generated_questions = generate_questions(title, required_skills, description)
        
        if "Invalid JSON format received from the model" in generated_questions["questions"]:
            return Response({"error": "Failed to generate valid questions"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        data = {"job": job.id, "questions": generated_questions["questions"]}
        serializer = GenerateQuestionSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




































# def generate_questions(job_field):

#     input_prompt = f'''
#     You are an AI assistant. Provide exactly 5 technical interview questions related to "{job_field}" in JSON format.
#     Strictly follow this format:
#     {{
#         "questions": [
#             "Question 1?",
#             "Question 2?",
#             "Question 3?",
#             "Question 4?",
#             "Question 5?"
#         ]
#     }}
#     '''

#     model = genai.GenerativeModel('gemini-1.5-flash')
#     response = model.generate_content([input_prompt])

#     if not response or not response.text.strip():
#         return {"questions": ["No valid response received from the model"]}

#     json_text = extract_json(response.text.strip())

#     try:
#         return json.loads(json_text) if json_text else {"questions": ["Invalid JSON format received from the model"]}
#     except json.JSONDecodeError:
#         return {"questions": ["Invalid JSON format received from the model"]}

# class GenerateQuestionView(APIView):

#     def post(self, request):
#         job_field = request.data.get("job_field")
#         if not job_field:
#             return Response({"error": "job_field is required"}, status=status.HTTP_400_BAD_REQUEST)

#         generated_questions = generate_questions(job_field)

#         if "Invalid JSON format received from the model" in generated_questions["questions"]:
#             return Response({"error": "Failed to generate valid questions"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         question_entry = GenerateQuestion.objects.create(
#             job_field=job_field,
#             questions=generated_questions["questions"]
#         )
#         serializer = GenerateQuestionSerializer(question_entry)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)