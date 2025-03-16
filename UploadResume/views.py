from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from resume.settings import GOOGLE_API_KEY
from GeneratedResume.models import Education, Project, Experience, TrainingCourse, Resume, Skill
from GeneratedResume.serializer import ResumeSerializer, UserSerializer
from decouple import config
from django.conf import settings  
from rest_framework.parsers import MultiPartParser, FormParser
import fitz
import re

User = get_user_model()

# Create your views here.
class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if "pdf_file" not in request.FILES:
            return Response({"error": "No PDF file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = request.FILES["pdf_file"]

        if pdf_file.size == 0:
            return Response({"error": "Uploaded file is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if pdf_file.content_type != "application/pdf":
            return Response({"error": "Uploaded file is not a valid PDF"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = pdf_file.read()
        if not pdf_data:
            return Response({"error": "Failed to read PDF file"}, status=status.HTTP_400_BAD_REQUEST)

        resume = Resume.objects.create(user=user, pdf_file=pdf_file)

        extracted_text = self.extract_text_from_pdf(pdf_data)

        parsed_data = self.parse_resume_data(extracted_text)

        if not isinstance(parsed_data, dict):  
            return Response({"error": "Failed to parse resume data correctly"}, status=status.HTTP_400_BAD_REQUEST)

        resume.summary = parsed_data.get("summary", "")

        for skill_name in parsed_data.get("skills", []):
            Skill.objects.create(resume=resume, skill=skill_name)

        for edu in parsed_data.get("education", []):
            if isinstance(edu, dict):
                Education.objects.create(
                    resume=resume, 
                    degree=edu.get("degree", ""),
                    institution=edu.get("institution", ""),
                    start_date=edu.get("start_date", ""),
                    end_date=edu.get("end_date", ""),
                    description=edu.get("description", "")
                )

        for proj in parsed_data.get("projects", []):
            if isinstance(proj, dict):
                Project.objects.create(
                    resume=resume, 
                    title=proj.get("title", ""),
                    description=proj.get("description", ""),
                    github_link=proj.get("github_link", None)
                )

        for exp in parsed_data.get("experiences", []):
            if isinstance(exp, dict):
                Experience.objects.create(
                    resume=resume, 
                    job_title=exp.get("job_title", ""),
                    company=exp.get("company", ""),
                    start_date=exp.get("start_date", ""),
                    end_date=exp.get("end_date", ""),
                    description=exp.get("description", "")
                )

        for course in parsed_data.get("trainings_courses", []):
            if isinstance(course, dict):
                TrainingCourse.objects.create(
                    resume=resume, 
                    title=course.get("title", ""),
                    institution=course.get("institution", ""),
                    start_date=course.get("start_date", ""),
                    end_date=course.get("end_date", ""),
                    description=course.get("description", "")
                )

        resume.save()
        serializer = ResumeSerializer(resume)

        return Response({
            "resume": serializer.data,
            "parsed_data": parsed_data
        }, status=status.HTTP_201_CREATED)

    def extract_text_from_pdf(self, pdf_data):
        doc = fitz.open(stream=pdf_data, filetype="pdf")  
        text = "\n".join(page.get_text("text") for page in doc)
        return text

    def parse_resume_data(self, resume_text):
        
        sections = {
            "summary": "",
            "skills": [],
            "education": [],
            "projects": [],
            "experiences": [],
            "trainings_courses": []
        }

        patterns = {
            "summary": r"(Summary|Objective)(.*?)(?=(Skills|Education|Experience|Projects|Certifications|$))",
            "skills": r"(Skills|Technical Skills)(.*?)(?=(Education|Experience|Projects|Certifications|$))",
            "education": r"(Education|Academic Background)(.*?)(?=(Experience|Projects|Certifications|$))",
            "projects": r"(Projects|Personal Projects)(.*?)(?=(Experience|Certifications|$))",
            "experiences": r"(Experience|Work Experience)(.*?)(?=(Projects|Certifications|$))",
            "trainings_courses": r"(Certifications|Courses|Trainings)(.*?)(?=$)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, resume_text, re.DOTALL | re.IGNORECASE)
            if match:
                extracted_text = match.group(2).strip()

                if key == "skills":
                    sections[key] = [skill.strip() for skill in extracted_text.split(",") if skill.strip()]
                elif key in ["education", "projects", "experiences", "trainings_courses"]:
                    items = extracted_text.split("\n") if extracted_text else []
                    sections[key] = [{"description": item.strip()} for item in items if item.strip()]
                else:
                    sections[key] = extracted_text.strip()

        print("Parsed Data:", sections)  
        return sections
