from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from GeneratedResume.models import Education, Project, Experience, TrainingCourse, Resume, Skill
from GeneratedResume.serializer import ResumeSerializer
import fitz  # PyMuPDF
import json
import re
import google.generativeai as genai
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes=[JWTAuthentication]
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
    
        extracted_text = self.extract_text_from_pdf(pdf_file.read())
    
        if not extracted_text.strip():
            return Response({"error": "Failed to extract text from PDF"}, status=status.HTTP_400_BAD_REQUEST)
    
        parsed_data = self.parse_resume_with_gemini(extracted_text)
    
        if not isinstance(parsed_data, dict) or not parsed_data:
            return Response({"error": "Failed to parse resume data correctly"}, status=status.HTTP_400_BAD_REQUEST)
    
        parsed_data.pop("email", None)  
        user.username = parsed_data.get("name", user.username)
        user.first_name = parsed_data.get("name", "").split(" ")[0] if parsed_data.get("name") else user.first_name
        user.last_name = " ".join(parsed_data.get("name", "").split(" ")[1:]) if parsed_data.get("name") else user.last_name
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

        education_entries = [Education(resume=resume, **edu) for edu in parsed_data.get("education", []) if isinstance(edu, dict)]
        Education.objects.bulk_create(education_entries)

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

        return Response({
            "resume": serializer.data,
            "parsed_data": parsed_data
        }, status=status.HTTP_201_CREATED)

    def extract_text_from_pdf(self, pdf_data):
        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text = "\n".join(page.get_text("text") for page in doc)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def parse_resume_with_gemini(self, resume_text):

        
        prompt = f"""
    Extract ATS-friendly resume data from the following text:
    {resume_text}
    
    Ensure the output is structured in **valid JSON format** with the following fields:
    - target_job_title (the desired job title)
    - name (full name of the person)
    - email
    - phone
    - location (city and country)
    - linkedin_link
    - github_link
    - summary
    - keywords (list of job-related keywords)
    - skills (list of relevant skills)
    - education (list of dicts with 'degree', 'institution', 'start_date', 'end_date', 'description')
    - work_experience (list of dicts with 'job_title', 'company', 'start_date', 'end_date', 'description')
    - certifications (list of dicts with 'title', 'institution', 'issue_date', 'expiry_date')
    - projects (list of dicts with 'title', 'description', 'github_link', 'technologies_used')
    - publications (list of dicts with 'title', 'journal', 'publication_date', 'link')
    
    Ensure all fields follow ATS-friendly formatting, using clear job-related keywords.
    """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt])

            response_text = response.text.strip()
            response_text = re.sub(r"```json|```", "", response_text).strip()

            if not response_text.startswith("{") or not response_text.endswith("}"):
                raise ValueError("The response is not a valid JSON structure.")

            parsed_data = json.loads(response_text)

            return parsed_data
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            return {"error": "Failed to parse resume data correctly"}
        except Exception as e:
            print(f"Error in Gemini API response: {e}")
            return {"error": str(e)}
