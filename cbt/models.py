"""Stores, Retrieves and Manages Data in Database Tables."""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy

from cbt.utils import u_p_path, u_s_path
from user.models import UserModel as User


RELATIONSHIPS = (
    ('F', 'Father'),
    ('M', 'Mother'),
    ('B', 'Brother'),
    ('S', 'Sister'),
    ('U', 'Uncle'),
    ('O', 'Others'),
)

SEMESTERS = (
    ("1", "First Semester"),
    ("2", "Second Semester"),
)

LEVELS = (
    ("100", "100 Level"),
    ("200", "200 Level"),
    ("300", "300 Level"),
    ("400", "400 Level"),
    ("500", "500 Level"),
)

'''
def display_semester(s):
    if int(s) == 1:
        return "First Semester"
    elif int(s) == 2:
        return "Second Semester"
    else: return s


def display_level(l):
    if int(l) == 100:
        return "100 Level"
    elif int(l) == 200:
        return "200 Level"
    elif int(l) == 300:
        return "300 Level"
    elif int(l) == 400:
        return "400 Level"
    elif int(l) == 500:
        return "500 Level"
    else: return l
'''


class Country(models.Model):
    """Stores list of counties of the world."""

    title = models.CharField(max_length=100, help_text="Name of country")

    class Meta:
        """Defines model meta attributes."""
        verbose_name_plural = 'countries'
        ordering = ['title']

    def __str__(self):
        """Returns human readable string of the country instance."""
        return self.title

    def get_states(self):
        """Returns list of states of the country instance."""
        return State.objects.filter(country=self.id)


class State(models.Model):
    """Stores list of states of countries."""

    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="country_name",
        help_text='Name of country'
    )
    title = models.CharField(max_length=100, help_text="Name of state")

    def __str__(self):
        """Returns human readable string of the state instance."""
        return self.title

    def get_lgas(self):
        """Returns list of Local Governmernt Areas (LGAs).

        Look up and return the list of LGAs of the state instance."""
        return LGA.objects.filter(state=self.id)


class LGA(models.Model):
    """Stores list of Local Governmernt Areas (LGAs) of states."""

    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name="state_name",
        help_text='Name of state.'
    )
    title = models.CharField(max_length=200, help_text="Name of LGA")

    def __str__(self):
        """Returns human readable string of the LGA instance."""
        return self.title


class Institution(models.Model):
    """Manages details of a given institution."""

    title = models.CharField(max_length=200, help_text='Name of institution')
    detail = models.TextField(help_text='Details of the institution')

    def __str__(self):
        """Returns human readable string of the institution."""
        return self.title


class Faculty(models.Model):
    """Manages details of a given faculty."""

    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="institution",
        help_text="Choose the institution"
    )
    title = models.CharField(max_length=200, help_text="Name of faculty")
    detail = models.TextField(help_text="Details of faculty")

    class Meta:
        """Defines meta attributes related to the model instance."""

        verbose_name_plural = 'faculties'

    def __str__(self):
        """Returns human readable string of the faculty instance."""
        return self.title


class Department(models.Model):
    """Manages details of a given department."""

    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="faculty",
        help_text="Choose the faculty"
    )
    title = models.CharField(max_length=200, help_text="Name of department")
    detail = models.TextField(help_text="Details of the faculty")

    def __str__(self):
        """Returns human readable string of the department instance."""
        return self.title


class Course(models.Model):
    """Store, retrieve and manage courses."""

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='department',
        help_text="Select department"
    )
    title = models.CharField(max_length=256, help_text="Course title")
    code = models.CharField(max_length=10, help_text="Course code")
    unit = models.SmallIntegerField("Course credit unit")
    detail = models.TextField(help_text="Details of the department")
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text='Generate token for what level?'
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text="Generate token for what semester?"
    )

    def __str__(self):
        """Returns human readable string of the course instance."""
        return self.title


class Question(models.Model):
    """Store, retrieve and manage questions."""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='course',
        help_text="Select course"
    )
    detail = models.CharField(max_length=500, help_text="Input question")
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text="What level is the question meant for?"
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text="What semester is the question meant for?"
    )
    option1 = models.CharField(max_length=800, help_text="Add option 1")
    option2 = models.CharField(max_length=800, help_text="Add option 2")
    option3 = models.CharField(
        max_length=800, help_text="Add option 3", blank=True
    )
    option4 = models.CharField(
        max_length=800, help_text="Add option 4", blank=True
    )
    option5 = models.CharField(
        max_length=800, help_text="Add option 5", blank=True
    )
    answer = models.PositiveSmallIntegerField(
        help_text='''Input the option that is the correct answer. eg: '1' for
        option1 or '2' for option2'''
    )
    score = models.PositiveSmallIntegerField(
        help_text="What is the score of this question?"
    )

    def __str__(self):
        """Returns human readable string of the question instance."""
        return self.detail


class Answer(models.Model):
    """Store, retrieve and manage answers."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="question",
        help_text="associated question"
    )
    answered_by = models.ForeignKey(
        "UserDetail", on_delete=models.CASCADE, related_name="student",
        help_text="Student username"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_answered",
        help_text="What course does this question belong to?"
    )
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text="What level is the answer meant for?"
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text="What semester is the answer meant for?"
    )
    user_answer = models.PositiveSmallIntegerField(
        help_text="Choose your answer", blank=True, null=True
    )
    is_answer = models.BooleanField(
        help_text="Is the answer correct?", blank=True, default=False
    )
    date = models.DateTimeField(
        help_text="When was this examination taken?", auto_now_add=True,
        editable=False
    )

    def get_question_option(self):
        """Return the correct question option based on user answer/choice."""
        if self.user_answer == 1:
            return self.question.option1
        elif self.user_answer == 2:
            return self.question.option2
        elif self.user_answer == 3:
            return self.question.option3
        elif self.user_answer == 4:
            return self.question.option4
        elif self.user_answer == 5:
            return self.question.option5
        else:
            return 'No answer choosen.'

    def get_semester(self):
        """Returns the readable semester choice."""
        return self.get_semester_display()  # display_semester(self.semester)

    def __str__(self):
        """Returns human readable string of the answer instance."""
        return self.get_question_option()


class CourseResult(models.Model):
    """Store, retrieve and manage course results."""

    user = models.ForeignKey(
        "UserDetail", on_delete=models.CASCADE, related_name="course_user",
        help_text="Student username"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="user_course",
        help_text="associated course"
    )
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text="What level is this course for?"
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text="What semester is this course for?"
    )
    score = models.SmallIntegerField(help_text="What is the score?")
    grade = models.CharField(
        max_length=2, help_text="What is the grade?", blank=True, null=True
    )

    def __str__(self):
        """Returns human readable string of the course result instance."""
        return str(self.score)


class Result(models.Model):
    """Store, retrieve and manage result."""

    user = models.ForeignKey(
        "UserDetail", on_delete=models.CASCADE, related_name="result",
        help_text="Student username"
    )
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text='What is your level.'
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text="What semester has this result?"
    )
    total_score = models.SmallIntegerField(
        help_text="Total score for the semester", blank=True, null=True
    )
    total_courses = models.PositiveSmallIntegerField(
        help_text="How many courses were offered in total?"
    )
    total_units = models.SmallIntegerField(
        help_text="Total units for the semester", blank=True, null=True
    )
    gpa = models.FloatField(
        null=True, help_text="What is the Grade Point Average (GPA)?"
    )
    date = models.DateTimeField(
        auto_now_add=True, editable=False,
        help_text="When was this result computed?"
    )

    def __str__(self):
        """Returns human readable string of the result instance."""
        return f'{self.get_semester_display()}: {self.total_score}'

    def get_courses(self):
        """Returns the courses used in computing the result."""
        return CourseResult.objects.filter(
            user=self.user, level=self.level, semester=self.semester
        )


class Programme(models.Model):
    """Student's programme details"""
    PROGRAMMES = (
        ("B.Sc", "Bachelor of Science"),
        ("B.Eng", "Bechelor of Engineering"),
        ("B.A", "Bachelor of Arts"),
    )
    STUDENT_MODES = (
        ("N", "New Student"),
        ("C", "Returning Student"),
        ("P", "Probation"),
        ("W", "Withrawal"),
    )
    ENTRY_MODES = (
        ("U", "UTME"),
        ("D", "Direct Entry"),
        ("T", "Transfer"),
        ("I", "IJAMB"),
    )
    STUDY_MODES = (
        ("F", "Full Time"),
        ("P", "Part Time"),
    )
    STUDENT_TYPES = (
        ("R", "Regular"),
        ("P", "Part Time"),
    )
    student = models.OneToOneField(
        "UserDetail", on_delete=models.CASCADE, unique=True,
        help_text='Username of registered student.'
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="programme",
        help_text="Your department", blank=True, null=True
    )
    programme = models.CharField(
        max_length=5, choices=PROGRAMMES, blank=True,
        help_text="Please select your Programme Type."
    )
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text="Please select your current level."
    )
    reg_no = models.CharField(
        max_length=30, blank=True, help_text="Enter your registration number."
    )
    jamb_no = models.CharField(
        max_length=30, blank=True,
        help_text="Enter your JAMB registration number."
    )
    student_mode = models.CharField(
        max_length=50, choices=STUDENT_MODES, blank=True,
        help_text="Student's mode"
    )
    student_type = models.CharField(
        max_length=50, choices=STUDENT_TYPES, blank=True,
        help_text="Student type"
    )
    entry_mode = models.CharField(
        max_length=50, choices=ENTRY_MODES, blank=True,
        help_text="Student's mode of entry."
    )
    study_mode = models.CharField(
        max_length=50, choices=STUDY_MODES, blank=True,
        help_text="Student's mode of study."
    )
    entry_year = models.SmallIntegerField(
        help_text="Admission year. (e.g. 2020)", blank=True, null=True
    )
    graduation_year = models.SmallIntegerField(
        help_text="Graduation year. (e.g. 2024)", blank=True, null=True
    )

    def __str__(self):
        """Returns human readable string of the programme instance."""
        return self.department or self.student.user.username


class Sponsor(models.Model):
    """Manages student's sponsor details."""

    name = models.CharField(
        max_length=250, blank=True,
        help_text="Enter sponsor's full name. Surname first."
    )
    student = models.OneToOneField(
        "UserDetail", on_delete=models.CASCADE, unique=True,
        help_text='Username of registered student.'
    )
    address = models.CharField(
        max_length=250, blank=True, help_text="Sponsor's address"
    )
    phone = models.IntegerField(
        help_text="Sponsor's mobile No.", null=True, blank=True
    )
    relationship = models.CharField(
        max_length=2, choices=RELATIONSHIPS, blank=True,
        help_text='How are you related?'
    )
    email = models.EmailField(help_text="Sponsor's Email", blank=True)

    def __str__(self):
        """Returns human readable string of the sponsor instance."""
        return self.student.user.username


class Kin(models.Model):
    """Manages student's Next of Kin details."""

    name = models.CharField(
        max_length=250, blank=True,
        help_text="Enter Next of Kin's full name. Surname first."
    )
    student = models.OneToOneField(
        "UserDetail", on_delete=models.CASCADE, unique=True,
        help_text='Username of registered student.'
    )
    address = models.CharField(
        max_length=250, blank=True, help_text="Next of Kin's Address"
    )
    phone = models.IntegerField(
        help_text="Next of Kin's mobile No.", null=True, blank=True
    )
    relationship = models.CharField(
        max_length=2, choices=RELATIONSHIPS, blank=True,
        help_text='How are you related?'
    )
    email = models.EmailField(help_text="Next of Kin's Email", blank=True)

    def __str__(self):
        """Returns human readable string of the sponsor instance."""
        return self.student.user.username


class UserDetail(models.Model):
    """Creates extra user details in the school database"""

    GENDERS = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('T', 'Transgender'),
        ('O', 'Others'),
        )
    RELIGIONS = (
        ('C', 'Christianity'),
        ('I', 'Islam'),
        ('T', 'Traditional'),
        ('H', 'Hinduism'),
        ('O', 'Others'),
        )
    STATUSES = (
        ("M", "Married"),
        ("E", "Engaged"),
        ("D", "Divorced"),
        ("S", "Single"),
        ("C", "Complicated"),
        ("O", "Others"),
        )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True,
        help_text='Username of registered user.'
    )
    middle_name = models.CharField(
        max_length=50, blank=True, help_text='middle name'
    )
    birth_date = models.DateTimeField(
        help_text='Date of birth', null=True, blank=True
    )
    email = models.EmailField(help_text='Email address', blank=True)
    gender = models.CharField(
        max_length=2, choices=GENDERS, blank=True,
        help_text='Please select your gender'
    )
    status = models.CharField(
        max_length=2, choices=STATUSES, blank=True,
        help_text='Please select your relationship status'
    )
    religion = models.CharField(
        max_length=2, choices=RELIGIONS, blank=True,
        help_text='Please select your religion'
    )
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name="state", blank=True,
        null=True, help_text='State of origin'
    )
    lga = models.ForeignKey(
        LGA, on_delete=models.CASCADE, related_name='lga', blank=True,
        null=True, help_text='Local Government Area of origin'
    )
    home_town = models.CharField(
        max_length=250, blank=True, help_text='Home town'
    )
    perm_address = models.CharField(
        max_length=300, blank=True, help_text='Permanent address'
    )
    phone = models.IntegerField(
        help_text='Your mobile phone number', null=True, blank=True
    )
    contact_address = models.CharField(
        max_length=300, blank=True, help_text='Contact address'
    )
    blood_group = models.CharField(
        max_length=10, blank=True, help_text='Blood group'
    )
    genotype = models.CharField(
        max_length=10, blank=True, help_text='Genotype'
    )
    signature = models.ImageField(
        upload_to=u_s_path, blank=True, help_text='Add your signature.'
    )
    pictures = models.ImageField(
        upload_to=u_p_path, blank=True, help_text='Select profile picture.'
    )
    last_modified = models.DateTimeField(
        help_text='Last modified date', auto_now=True
    )

    def __str__(self):
        """Returns human readable string of the user detail instance."""
        return self.user.username

    def full_name(self):
        """Returns user's full name."""
        if self.user.get_full_name():
            return f'{self.user.get_full_name()} {self.middle_name}'.strip()
        else:
            return self.user.username.strip()

    def get_absolute_url(self):
        """Returns unique URL for user account instance."""
        return reverse_lazy('profile', args=[self.user.username])


class Token(models.Model):
    """Generate random token unique for each User and Course.

    This model represents random tokens generated for each course a student
    studies. The token is unique to a given user and for a given course.
    It is required for a Student to be able to take part in any and every
    examination.

    All the fields are required and each field itself is self explanatory."""

    user = models.ForeignKey(
        UserDetail, on_delete=models.CASCADE, related_name='user_token',
        help_text='Generate Token for user'
    )
    token = models.CharField(max_length=250, help_text='Access token')
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100,
        help_text='Generate token for what level?'
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text='Generate token for what semester?'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='token_course',
        help_text='Generate token for what course?'
    )

    class Meta:
        """Defines meta attributes for the model."""

        permissions = (
            ("create_token", "Can create token for users"),
            ("flush_token", "Can flush/delete tokens"),
        )

    def __str__(self):
        """Returns human readable string of the token instance."""
        return self.token


class UserCourse(models.Model):
    """Courses a Student can study.

    Each course must be registered before the user can study it or atleast
    take exams and test/assignment on the course."""

    user = models.ForeignKey(
        UserDetail, on_delete=models.CASCADE, related_name='register_course',
        help_text='Student registering course'
    )
    level = models.CharField(
        max_length=3, choices=LEVELS, default=100, help_text="Student's level"
    )
    semester = models.CharField(
        max_length=2, choices=SEMESTERS, default=1,
        help_text="Student's semester"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='registered_course',
        help_text='What course are you registering?'
    )

    def __str__(self):
        """Returns human readable string of the user course instance."""
        return str(self.course)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserDetail.objects.create(user=instance)


@receiver(post_save, sender=UserDetail)
def create_profile_members(sender, instance, created, **kwargs):
    if created:
        Kin.objects.create(student=instance)
        Sponsor.objects.create(student=instance)
        Programme.objects.create(student=instance)
