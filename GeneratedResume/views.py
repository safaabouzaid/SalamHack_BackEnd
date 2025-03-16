from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from resume.settings import GOOGLE_API_KEY
from .models import Education, Project, Experience, TrainingCourse, Resume, Skill
from .serializer import ResumeSerializer, UserSerializer
from decouple import config
import google.generativeai as genai
from django.conf import settings  
User = get_user_model()

genai.configure(api_key="AIzaSyAWfqk0NLuH3FV8BJgI1RtGQYoRxIR46sM")

class ResumeAPIView(APIView):
    def post(self, request):
        user_data = request.data

        user, created = User.objects.get_or_create(
            username=user_data.get("username"),
            email=user_data.get("email"),
            phone= user_data.get("phone"),
            location= user_data.get("location"),
            github_link=user_data.get('github_link'),
            linkedin_link=user_data.get('linkedin_link'),
        
        )
        if created:
            user.set_password(user_data.get("password", "default_password"))
            user.save()

        profile_summary = self.generate_summary(user_data)
        
        resume = Resume.objects.create(
            user=user,
            summary=profile_summary,
            
        )

        skill_objects = [Skill(resume=resume, skill=skill["skill"], level=skill.get("level")) for skill in user_data.get("skills", [])]
        Skill.objects.bulk_create(skill_objects)
        
        education_objects = [Education(resume=resume, **edu) for edu in user_data.get("education", [])]
        Education.objects.bulk_create(education_objects)
        
        project_objects = [Project(resume=resume, **proj) for proj in user_data.get("projects", [])]
        Project.objects.bulk_create(project_objects)
        
        experience_objects = [Experience(resume=resume, **exp) for exp in user_data.get("experiences", [])]
        Experience.objects.bulk_create(experience_objects)
        
        training_objects = [TrainingCourse(resume=resume, **training) for training in user_data.get("trainings_courses", [])]
        TrainingCourse.objects.bulk_create(training_objects)

        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def generate_summary(self, user_data):
        skills_text = ", ".join([skill.get('skill', 'N/A') for skill in user_data.get('skills', [])])
        education_text = "; ".join(
            [f"{edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')} ({edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')})"
             for edu in user_data.get('education', [])]
        )

        prompt = f"""
        Generate a professional and impactful resume summary in the first person, emphasizing my problem-solving skills, leadership, and teamwork. Focus on the following:
        - My key technical skills: {skills_text}
        - My educational achievements and highlights: {education_text}
        Ensure the summary is concise, ATS-optimized, and aligned with software development roles.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt])
        return response.text.strip()




########///////////ResumeUploadView///////#####
class ResumeUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)  

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id) 
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

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
        self.parse_resume_data(resume, extracted_text)

        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def extract_text_from_pdf(self, pdf_data):
        """ استخراج النصوص من ملف PDF """
        doc = fitz.open(stream=pdf_data, filetype="pdf")  
        text = ""
        for page in doc:  
            text += page.get_text("text") + "\n"  
        return text
