from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from .models import Answer, UserDetail, Kin, Sponsor, Course, Question, Result, Programme, Token, UserCourse


class RegisterUserForm(ModelForm):
    password = forms.CharField(max_length=200, min_length=6, help_text="Choose your password", widget=forms.PasswordInput)
    verify_password = forms.CharField(max_length=200, min_length=6, help_text="Confirm your password", widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        
    
    def clean_verify_password(self):
        data = self.cleaned_data["verify_password"]
        user_pass = self.cleaned_data["password"]
        if not data == user_pass:
            raise forms.ValidationError(_("Invalid passwords: Password and Verify Password didn't match. Please enter the same password in both fields."))
        
        return data


'''
class AnswerForm(ModelForm):
    """Form for choosing answers for list of questions."""
    class Meta:
        model = Answer
        fields = "__all__"
'''

class EditUserDetailForm(ModelForm):
    """Form for editing more user details."""
    class Meta:
        model = UserDetail
        exclude = ["user", "last_modified"]


class EditKinForm(ModelForm):
    """Form for edting next of kin's details."""
    class Meta:
        model = Kin
        exclude = ["student"]


class EditSponsorForm(ModelForm):
    """Form for editing Sponsor's details."""
    class Meta:
        model = Sponsor
        exclude = ["student"]


class EditProgrammeForm(ModelForm):
    """Form for editing Student's programme details."""
    class Meta:
        model = Programme
        exclude = ["student"]


class CompileResultForm(ModelForm):
    """Form for chosing which examination results to compile."""
    class Meta:
        model = Result
        fields = ["level", "semester"]


class ChooseQuestionForm(ModelForm):
    """Form for chosing which examination questions to take."""
    class Meta:
        model = Question
        fields = ["course", "level", "semester"]

    

class AddQuestionForm(ChooseQuestionForm):
    """Implements all ChooseQuestionForm fields with additional total field."""
    total = forms.IntegerField(label="Number of questions to add.", min_value=1, max_value=100, initial=10)


class LevelResultForm(ModelForm):
    """Form for selecting which level result to view"""
    class Meta:
        model = Result
        fields = ["level"]


class GenerateTokenForm(ModelForm):
    """Form for generating random tokens required in order to participate in an exam.

    All fields are required."""
    
    class Meta:
        model = Token
        exclude = ["user", "token"]


class RegisterCourseForm(ModelForm):
    """Form for registering courses a student can study for the semester."""
    class Meta:
        model = UserCourse
        fields = "__all__"


class ChooseExamForm(ModelForm):
    """Form for selecting which examination to take with token verification field included."""
    class Meta:
        model = Token
        exclude = ["user"]