from django.shortcuts import render
import google.generativeai as genai
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Job
from GeneratedResume.models import Resume
from GeneratedResume.serializer import ResumeSerializer
from .serializer import JobSerializer
import json


class JobRecommendationView(APIView):
    def get(self, request, user_id):
        try:
            # 
            resume = Resume.objects.filter(user_id=user_id).first()
            if not resume:
                return Response({"error": "Resume not found"}, status=404)

            resume_data = ResumeSerializer(resume).data

            skills = ", ".join([skill["skill"] for skill in resume_data.get("skills", [])])
            experiences = ", ".join([exp["job_title"] for exp in resume_data.get("experiences", [])])

            jobs = Job.objects.all()
            job_data = [{"title": job.title, "required_skills": job.required_skills, "description": job.description} for job in jobs]

            prompt = f"""
            Act as an AI job recommender.
            The user has the following skills: {skills} and work experience: {experiences}.
            Here is a list of available job opportunities:
            {json.dumps(job_data, ensure_ascii=False)}

            Return ONLY a JSON array in the following format:
            [
                {{"job_title": "Job Title", "match_percentage": 95}},
                {{"job_title": "Job Title", "match_percentage": 85}}
            ]
            STRICTLY return only valid JSON output, with no additional explanations, notes, or formatting.
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            response_text = response.text.strip().strip("```json").strip("```")

            print("AI Response:", response_text)

            try:
                recommendations = json.loads(response_text)
            except json.JSONDecodeError:
                return Response({"error": "Invalid response from AI", "raw_response": response_text}, status=500)

            return Response({"recommendations": recommendations})

        except Exception as e:
            return Response({"error": str(e)}, status=500)
