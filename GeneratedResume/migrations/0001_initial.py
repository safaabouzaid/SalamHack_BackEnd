# Generated by Django 5.1.6 on 2025-03-13 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(blank=True, null=True)),
                ('github_link', models.URLField(blank=True, null=True)),
                ('linkedin_link', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('github_link', models.URLField(blank=True, null=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='GeneratedResume.resume')),
            ],
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('start_date', models.CharField(blank=True, max_length=20, null=True)),
                ('end_date', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='GeneratedResume.resume')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.CharField(max_length=255)),
                ('institution', models.CharField(max_length=255)),
                ('start_date', models.CharField(blank=True, max_length=20, null=True)),
                ('end_date', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='GeneratedResume.resume')),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.CharField(max_length=255)),
                ('level', models.CharField(blank=True, max_length=50, null=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='GeneratedResume.resume')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('institution', models.CharField(max_length=255)),
                ('start_date', models.CharField(blank=True, max_length=20, null=True)),
                ('end_date', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainings_courses', to='GeneratedResume.resume')),
            ],
        ),
        migrations.AddField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to='GeneratedResume.user'),
        ),
    ]
