# Generated by Django 5.1.6 on 2025-03-16 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GeneratedResume', '0008_remove_resume_github_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
