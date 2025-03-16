from django.contrib import admin
from .models import Resume,User,Skill,Education,Project,Experience,TrainingCourse
# Register your models here.
admin.site.register(User)
admin.site.register(Resume)
admin.site.register(Skill)
admin.site.register(Education)
admin.site.register(Project)
admin.site.register(Experience)
admin.site.register(TrainingCourse)


