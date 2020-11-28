"""Register the needed models.

Register models with the Django Admin to enable easy administration."""

from django.contrib import admin
from cbt.models import (
    Answer, Country, Course, Department, Faculty, Kin, LGA, Programme,
    Question, Institution, Sponsor, State, UserDetail
)


admin.site.register(Country)
admin.site.register(State)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Faculty)
admin.site.register(Institution)
admin.site.register(Department)
admin.site.register(UserDetail)
admin.site.register(Sponsor)
admin.site.register(Kin)
admin.site.register(Course)
admin.site.register(LGA)
admin.site.register(Programme)
