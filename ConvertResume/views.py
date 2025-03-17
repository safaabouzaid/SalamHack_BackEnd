from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from GeneratedResume.models import Education, Project, Experience, TrainingCourse, Resume, Skill
from GeneratedResume.serializer import ResumeSerializer
import fitz  # PyMuPDF
import json
import re
import google.generativeai as genai

class ConvertResumeAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
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

        resume = self.generate_ats_resume(parsed_data)

        ats_resume = {
         "name": parsed_data.get("name", ""),
         "phone": parsed_data.get("phone", ""),
         "email": parsed_data.get("email", ""),
         "location": parsed_data.get("location", ""),
         "summary": self.generate_summary(parsed_data),
         "skills": parsed_data.get("skills", []),
         "education": parsed_data.get("education", []),
         "projects": parsed_data.get("projects", []),
         "experiences": parsed_data.get("experiences", []),
         "trainings_courses": parsed_data.get("trainings_courses", []),
}
        return Response(ats_resume, status=status.HTTP_201_CREATED)

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
        Extract structured resume data from the following text:
        {resume_text}
        
        Provide the response in a structured JSON format with the following fields:
        - name, phone, location, email, github_link, linkedin_link, summary
        - skills (list), education (list), projects (list), experiences (list), trainings_courses (list)
        Ensure the response is in valid JSON format.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt])

            response_text = re.sub(r"```json|```", "", response.text.strip()).strip()
            return json.loads(response_text) if response_text.startswith("{") and response_text.endswith("}") else {}
        except Exception as e:
            print(f"Error in Gemini API response: {e}")
            return {}

    def generate_ats_resume(self, parsed_data):
        resume = Resume.objects.create(
            summary=self.generate_summary(parsed_data)
        )

        Skill.objects.bulk_create([Skill(resume=resume, skill=s) for s in parsed_data.get("skills", []) if isinstance(s, str)])

        Education.objects.bulk_create([
            Education(
                resume=resume,
                degree=edu.get("degree", "Unknown"),
                institution=edu.get("institution", "Unknown"),
                start_date=edu.get("start_date", ""),
                end_date=edu.get("end_date", "")
            ) for edu in parsed_data.get("education", []) if isinstance(edu, dict)
        ])

        Project.objects.bulk_create([
            Project(
                resume=resume,
                title=proj.get("name", "Untitled"),
                github_link=proj.get("link", ""),
                description=proj.get("description", "")
            ) for proj in parsed_data.get("projects", []) if isinstance(proj, dict)
        ])

        Experience.objects.bulk_create([
            Experience(
                resume=resume,
                job_title=exp.get("title", "Unknown"),
                company=exp.get("location", "Unknown"),
                start_date=exp.get("years", "").split("-")[0] if "years" in exp else "",
                end_date=exp.get("years", "").split("-")[1] if "years" in exp else "",
                description=exp.get("description", "")
            ) for exp in parsed_data.get("experiences", []) if isinstance(exp, dict)
        ])

        TrainingCourse.objects.bulk_create([
            TrainingCourse(
                resume=resume,
                course_name=course.get("name", "Unknown"),
                institution=course.get("institution", "Unknown"),
                completion_date=course.get("completion_date", "")
            ) for course in parsed_data.get("trainings_courses", []) if isinstance(course, dict)
        ])

        return resume

    def generate_summary(self, parsed_data):
        skills_text = ", ".join(parsed_data.get("skills", []))
        education_text = "; ".join(
            [f"{edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')} ({edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')})"
             for edu in parsed_data.get("education", [])]
        )

        prompt = f"""
        Generate a professional and ATS-optimized resume summary based on:
        - Skills: {skills_text}
        - Education: {education_text}
        Keep it concise and impactful.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt])
        return response.text.strip()