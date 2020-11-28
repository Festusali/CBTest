from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.forms import CreateUserForm, ChangeUserForm
from user.models import UserModel


class CustomUserAdmin(UserAdmin):
    add_form = CreateUserForm
    form = ChangeUserForm
    model = UserModel
    list_display = ['username', 'email', ]


admin.site.register(UserModel, CustomUserAdmin)
