from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
import os
import google.generativeai as genai
from decouple import config
#api_key = config('API_KEY')
#genai.configure(api_key="AIzaSyC_7sXsoqlmDMWVysUZQn1SUa4-KkAYlyw")
genai.configure(api_key=config('API_KEY'))

class ResumeAPIView(APIView):
    def post(self, request):
        user_data = request.data

        profile_summary = self.generate_summary(user_data)
        user_data['profile_summary'] = profile_summary

        pdf_path = self.generate_resume(user_data)

        try:
            with open(pdf_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="generated_resume.pdf"'
            return response
        finally:
            os.remove(pdf_path)

    def generate_summary(self, user_data):
        skills_text = ", ".join([skill.get('skill', 'N/A') for skill in user_data.get('skills', [])])
        education_text = "; ".join(
            [f"{edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')} ({edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')})" 
             for edu in user_data.get('education', [])]
        )
        projects_text = "; ".join(
            [f"{project.get('title', 'N/A')} ({project.get('description', 'N/A')})" 
             for project in user_data.get('projects', [])]
        )

        prompt = f"""
        Generate a professional and impactful resume summary in the first person, emphasizing my problem-solving skills, leadership, and teamwork. Focus on the following:
- My key technical skills: {skills_text}
- My educational achievements and highlights: {education_text}
Ensure the summary is concise, ATS-optimized, and aligned with software development roles.
"""

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt])
        summary = response.text.strip()
        return summary

    def generate_resume(self, user_data):
        pdf_file = "generated_resume.pdf"
        pdf_path = os.path.join(os.getcwd(), pdf_file)
        document = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Header
        name = user_data.get('name', 'N/A')
        email = user_data.get('email', 'N/A')
        phone = user_data.get('phone', 'N/A')
        location = user_data.get('location', 'N/A')

        story.append(Paragraph(name, styles['Title']))
        story.append(Paragraph(f"Email: {email} | Phone: {phone} | Location: {location}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Summary
        profile_summary = user_data.get('profile_summary', 'No profile summary provided.')
        story.append(Paragraph("Summary", styles['Heading2']))
        story.append(Paragraph(profile_summary, styles['Normal']))
        story.append(Spacer(1, 12))

        # Skills 
        skills = user_data.get('skills', [])
        story.append(Paragraph("Skills", styles['Heading2']))
        if skills:
            for skill in skills:
                story.append(Paragraph(f"- {skill.get('skill', 'N/A')} (Level: {skill.get('level', 'N/A')})", styles['Normal']))
        else:
            story.append(Paragraph("No skills provided.", styles['Normal']))
        story.append(Spacer(1, 12))

        # Education
        education = user_data.get('education', [])
        story.append(Paragraph("Education", styles['Heading2']))
        if education:
            for edu in education:
                edu_text = f"{edu.get('degree', 'N/A')} at {edu.get('institution', 'N/A')} ({edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')})"
                story.append(Paragraph(edu_text, styles['Normal']))
                story.append(Paragraph(edu.get('description', 'N/A'), styles['Normal']))
        else:
            story.append(Paragraph("No education details provided.", styles['Normal']))
        story.append(Spacer(1, 12))

        # Courses
        courses = user_data.get('courses', [])
        story.append(Paragraph("Courses", styles['Heading2']))
        if courses:
            for course in courses:
                course_text = f"{course.get('course_name', 'N/A')} on {course.get('platform', 'N/A')} ({course.get('start_date', 'N/A')} - {course.get('end_date', 'N/A')})"
                story.append(Paragraph(course_text, styles['Normal']))
        else:
            story.append(Paragraph("No courses provided.", styles['Normal']))
        story.append(Spacer(1, 12))

        # Internships
        internships = user_data.get('internships', [])
        story.append(Paragraph("Internships", styles['Heading2']))
        if internships:
            for internship in internships:
                internship_text = f"{internship.get('title', 'N/A')} at {internship.get('company', 'N/A')} ({internship.get('duration', 'N/A')})"
                story.append(Paragraph(internship_text, styles['Normal']))
        else:
            story.append(Paragraph("No internships provided.", styles['Normal']))
        story.append(Spacer(1, 12))

        # Projects
        projects = user_data.get('projects', [])
        story.append(Paragraph("Projects", styles['Heading2']))
        if projects:
            for project in projects:
                project_text = f"{project.get('title', 'N/A')} - {project.get('description', 'N/A')}"
                story.append(Paragraph(project_text, styles['Normal']))
                if project.get('project_link'):
                    story.append(Paragraph(f"Link: {project.get('project_link', 'N/A')}", styles['Normal']))
        else:
            story.append(Paragraph("No projects provided.", styles['Normal']))

        document.build(story)
        return pdf_path
