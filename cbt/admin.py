from django.contrib import admin
from .models import Faculty, School, Department, Course, Question, Answer, UserDetail, Kin, Sponsor, LGA, Programme

# Register your models here.
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Faculty)
admin.site.register(School)
admin.site.register(Department)
admin.site.register(UserDetail)
admin.site.register(Sponsor)
admin.site.register(Kin)
admin.site.register(Course)
admin.site.register(LGA)
admin.site.register(Programme)

