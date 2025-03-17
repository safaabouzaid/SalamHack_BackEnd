from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import   Resume,ResumeEvaluation
from .serializer import ResumeEvaluationSerializer
import google.generativeai as genai
from decouple import config
from django.shortcuts import get_object_or_404
import os
import json

# Create your views here.

def evaluate_resume(resume, job_description):
    input_prompt = f'''
    Act as an ATS system with expertise in software engineering, data science, and related fields.
    Evaluate the resume based on the job description and return the match percentage,
    missing keywords, and improvement tips in **valid JSON format ONLY**.

    Resume: {resume.summary}
    Job Description: {job_description}

    Ensure the response is **pure JSON**, without extra text, and follows this structure:
    {{
        "JD Match": 0.0,
        "MissingKeywords": [],
        "ImprovementTips": ""
    }}
    '''

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt])

    if not response or not response.text.strip():
        return {
            "JD Match": 0,
            "MissingKeywords": [],
            "ImprovementTips": "No valid response received from the model"
        }

    #حتى مايرجعلي أي نص اضافي بالريسبونس
    json_text = response.text.strip().strip("```json").strip("```") 
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return {
            "JD Match": 0,
            "MissingKeywords": [],
            "ImprovementTips": "Invalid JSON format received from the model"
        }


class ResumeEvaluationView(APIView):
    def post(self, request, resume_id):
        resume = get_object_or_404(Resume, id=resume_id)
        job_description = request.data.get("job_description",)
        evaluation_result = evaluate_resume(resume, job_description)
        
        evaluation = ResumeEvaluation.objects.create(
            resume=resume,
            job_description=job_description,
            match_percentage=evaluation_result["JD Match"],
            missing_keywords=evaluation_result["MissingKeywords"],
            improvement_tips=evaluation_result["ImprovementTips"]
        )
        
        serializer = ResumeEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
