from rest_framework import serializers
from .models import User, Resume, Skill, Education, Project, Experience, TrainingCourse

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'location','github_link', 'linkedin_link']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill', 'level']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_date', 'end_date', 'description']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_link']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'description']

class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = ['title', 'institution', 'start_date', 'end_date', 'description']

class ResumeSerializer(serializers.ModelSerializer):
    personal_details = UserSerializer(source='user')
    skills = SkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    trainings_courses = TrainingCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = ['id','personal_details', 'summary', 'skills', 'education', 'projects', 'experiences', 'trainings_courses']











