from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Education, Project,Experience,TrainingCourse,Resume,Skill
from decouple import config
import google.generativeai as genai

User = get_user_model()

genai.configure(api_key=config('API_KEY'))
class ResumeAPIView(APIView):
    def post(self, request):
        user_data = request.data

        user, created  = User.objects.get_or_create(
            email=user_data.get("email", f"guest_{User.objects.count()}@example.com"),
            defaults={
                 "username": user_data.get("username", f"guest_{User.objects.count()}"),
                "phone": user_data.get("phone", ""),
                "location": user_data.get("location", ""),
            }
        )
        if created:
          user.set_password(user_data.get("password", "default_password"))
          user.save()

        profile_summary = self.generate_summary(user_data)

        resume = Resume.objects.create(
            user=user,
            summary=profile_summary,
            github_link=user_data.get('github_link'),
            linkedin_link=user_data.get('linkedin_link'),
        )

        for skill in user_data.get("skills", []):
            Skill.objects.create(resume=resume, skill=skill.get('skill'), level=skill.get('level'))

        for edu in user_data.get("education", []):
            Education.objects.create(resume=resume, degree=edu.get('degree'), institution=edu.get('institution'),
                                     start_date=edu.get('start_date'), end_date=edu.get('end_date'), description=edu.get('description'))

        for proj in user_data.get("projects", []):
            Project.objects.create(resume=resume, title=proj.get('title'), description=proj.get('description'),
                                   github_link=proj.get('github_link'))

        for exp in user_data.get("experiences", []):
            Experience.objects.create(resume=resume, job_title=exp.get('job_title'), company=exp.get('company'),
                                      start_date=exp.get('start_date'), end_date=exp.get('end_date'), description=exp.get('description'))

        for training_course in user_data.get("trainings_courses", []):
            TrainingCourse.objects.create(resume=resume, title=training_course.get('title'), institution=training_course.get('institution'),
                                          start_date=training_course.get('start_date'), end_date=training_course.get('end_date'), description=training_course.get('description'))

        return Response({
            "resume_id": resume.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "location": user.location,
            },
            "summary": resume.summary,
            "github_link": resume.github_link,
            "linkedin_link": resume.linkedin_link,
            "skills": [{"skill": s.skill, "level": s.level} for s in resume.skills.all()],
            "education": [{"degree": e.degree, "institution": e.institution, "start_date": e.start_date, "end_date": e.end_date, "description": e.description} for e in resume.education.all()],
            "projects": [{"title": p.title, "description": p.description, "github_link": p.github_link} for p in resume.projects.all()],
            "experiences": [{"job_title": ex.job_title, "company": ex.company, "start_date": ex.start_date, "end_date": ex.end_date, "description": ex.description} for ex in resume.experiences.all()],
            "trainings_courses": [{"title": tc.title, "institution": tc.institution, "start_date": tc.start_date, "end_date": tc.end_date, "description": tc.description} for tc in resume.trainings_courses.all()],
        })

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

