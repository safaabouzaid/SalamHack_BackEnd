from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from GeneratedResume.models import Education, Project, Experience, TrainingCourse, Resume, Skill
from .models import ResumeEvaluation
from GeneratedResume.serializer import ResumeSerializer
from .serializer import ResumeEvaluationSerializer
import fitz  # PyMuPDF
import json
import re
import google.generativeai as genai
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_data):
        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in doc)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

class ResumeEvaluationView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        user = request.user

        if "pdf_file" not in request.FILES:
            return Response({"error": "No PDF file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = request.FILES["pdf_file"]

        if pdf_file.size == 0:
            return Response({"error": "Uploaded file is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if pdf_file.content_type != "application/pdf":
            return Response({"error": "Uploaded file is not a valid PDF"}, status=status.HTTP_400_BAD_REQUEST)

        extracted_text = PDFProcessor.extract_text_from_pdf(pdf_file.read())

        if not extracted_text.strip():
            return Response({"error": "Failed to extract text from PDF"}, status=status.HTTP_400_BAD_REQUEST)

        parsed_data = self.parse_resume_with_gemini(extracted_text)

        if not isinstance(parsed_data, dict) or not parsed_data:
            return Response({"error": "Failed to parse resume data correctly"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.username = parsed_data.get("name", user.username)
        user.first_name = parsed_data.get("name", "").split(" ")[0] if parsed_data.get("name") else user.first_name
        user.last_name = " ".join(parsed_data.get("name", "").split(" ")[1:]) if parsed_data.get("name") else user.last_name
        user.email = parsed_data.get("email", user.email)
        user.phone = parsed_data.get("phone", user.phone)
        user.location = parsed_data.get("location", user.location)
        user.github_link = parsed_data.get("github_link", user.github_link)
        user.linkedin_link = parsed_data.get("linkedin_link", user.linkedin_link)
        user.save()

        resume = Resume.objects.create(
            user=user,
            summary=parsed_data.get("summary", ""),
            pdf_file=pdf_file
        )

        skills = [Skill(resume=resume, skill=skill) for skill in parsed_data.get("skills", []) if isinstance(skill, str)]
        Skill.objects.bulk_create(skills)

        education_objects = []
        allowed_fields = {field.name for field in Education._meta.fields if field.name != "id"}
        for edu in parsed_data.get("education", []):
            if isinstance(edu, dict):
                filtered_edu = {key: value for key, value in edu.items() if key in allowed_fields}
                education_objects.append(Education(resume=resume, **filtered_edu))

        Education.objects.bulk_create(education_objects)

        allowed_fields = {field.name for field in Project._meta.fields if field.name != "id"}
        project_objects = []
        for proj in parsed_data.get("projects", []):
            if isinstance(proj, dict):
                filtered_proj = {key: value for key, value in proj.items() if key in allowed_fields}
                project_objects.append(Project(resume=resume, **filtered_proj))
        Project.objects.bulk_create(project_objects)  

        experiences = [Experience(resume=resume, **exp) for exp in parsed_data.get("experiences", []) if isinstance(exp, dict)]
        Experience.objects.bulk_create(experiences)

        training_courses = [TrainingCourse(resume=resume, **course) for course in parsed_data.get("trainings_courses", []) if isinstance(course, dict)]
        TrainingCourse.objects.bulk_create(training_courses)

        resume.save()
        serializer = ResumeSerializer(resume)

        job_description = request.data.get("job_description", "")
        evaluation_result = self.evaluate_resume(resume, job_description) if job_description else None
        evaluation_data = {}
        
        if evaluation_result:
            evaluation = ResumeEvaluation.objects.create(
                resume=resume,
                job_description=job_description,
                match_percentage=evaluation_result["JD Match"],
                missing_keywords=evaluation_result["MissingKeywords"],
                improvement_tips=evaluation_result["ImprovementTips"]
            )
            
        return Response({
             "match_percentage": evaluation_result["JD Match"],
             "missing_keywords": evaluation_result["MissingKeywords"],
             "improvement_tips": evaluation_result["ImprovementTips"]
         }, status=status.HTTP_201_CREATED)


    def parse_resume_with_gemini(self, resume_text):
        prompt = f"""
        Extract ATS-friendly resume data from the following text:
        {resume_text}
        Ensure the output is structured in **valid JSON format** with the required fields.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt])
            response_text = response.text.strip().strip("```json").strip("```")
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return {}

    def evaluate_resume(self, resume, job_description):
        input_prompt = f'''
        Act as an ATS system and evaluate the resume based on the job description.
        Return the match percentage, missing keywords, and improvement tips in **valid JSON format ONLY**.
        Resume: {resume.summary}
        Job Description: {job_description}
        Ensure the response follows this structure:
        {{
            "JD Match": 0.0,
            "MissingKeywords": [],
            "ImprovementTips": ""
        }}
        '''
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_prompt])
        json_text = response.text.strip().strip("```json").strip("```")
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return {"JD Match": 0, "MissingKeywords": [], "ImprovementTips": "Invalid JSON format received from the model"}