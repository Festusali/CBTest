from django import forms
from django.forms import ModelForm

from cbt.models import Question, Result, Token, UserCourse


'''class AnswerForm(ModelForm):
    """Form for choosing answers for list of questions."""
    class Meta:
        model = Answer
        fields = "__all__"
'''


class CompileResultForm(ModelForm):
    """Form for chosing which examination results to compile."""

    class Meta:
        model = Result
        fields = ["level", "semester"]


class ChooseCourseForm(ModelForm):
    """Form for selecting among listt of courses."""

    class Meta:
        model = Question
        fields = ["course"]


class AddQuestionForm(ModelForm):
    """Form for selecting course and the number of questions to add."""

    total = forms.IntegerField(
        label="Number of questions to add.", min_value=1, max_value=30,
        initial=10
    )

    class Meta:
        model = Question
        fields = ['course']


class LevelResultForm(ModelForm):
    """Form for selecting which level result to view"""

    class Meta:
        model = Result
        fields = ["level"]


class GenerateTokenForm(ModelForm):
    """Form for generating random exam tokens.

    For each exam, a unique token is generated. This form allows to generate
    token for a given examination.

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
    """Allows to choose the exam to seat for."""

    class Meta:
        model = Token
        fields = ["course", "token"]
