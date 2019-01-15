from django.db import models
from django.contrib.auth.models import User


def u_p_path(instance, filename):
    #Profile picture will be uploaded to "images/user_pictures/[instance.username]"

    username = User.objects.get(pk=instance.user_id)
    return "images/user_pictures/{}.png".format(username)


def u_s_path(instance, filename):
    #Profile picture will be uploaded to "images/user_pictures/[instance.username]"

    username = User.objects.get(pk=instance.user_id)
    return "images/user_signatures/{}.png".format(username)


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



# Create your models here.
class Country(models.Model):
    title = models.CharField(max_length=200, help_text="Name of country")

    def __str__(self):
        return self.title
    
    def get_states(self):
        return State.objects.filter(country=self.id)


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="contry_name", help_text='Name of country.')
    title = models.CharField(max_length=200, help_text="Name of state.")

    def __str__(self):
        return self.title
    
    def get_lgas(self):
        return LGA.objects.filter(state=self.id)


class LGA(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="state_name", help_text='Name of state.')
    title = models.CharField(max_length=200, help_text="Name of local government area.")

    def __str__(self):
        return self.title


class School(models.Model):
    title = models.CharField(max_length=200, help_text="Name of university")
    detail = models.TextField(help_text="Details of the University")

    def __str__(self):
        return self.title


class Faculty(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="University", help_text="Choose the University")
    title = models.CharField(max_length=200, help_text="Name of Faculty")
    detail = models.TextField(help_text="Details of faculty")

    def __str__(self):
        return self.title



class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="faculty", help_text="Choose the faculty")
    title = models.CharField(max_length=200, help_text="Name of Department")
    detail = models.TextField(help_text="Details of the faculty")

    def __str__(self):
        return self.title



class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department', help_text="Select Department")
    title = models.CharField(max_length=256, help_text="Course Title")
    code = models.CharField(max_length=10, help_text="Course Code")
    unit = models.SmallIntegerField("Course Credit Unit")
    detail = models.TextField(help_text="Details of the department")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text='Generate token for what level?')
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="Generate token for what semester?")
    

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course', help_text="Select course")
    detail = models.CharField(max_length=500, help_text="Input question")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text="What level is the question meant for?")
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="What semester is the question meant for?")
    option1 = models.CharField(max_length=800, help_text="Input option 1", blank=True)
    option2 = models.CharField(max_length=800, help_text="Input option 2", blank=True)
    option3 = models.CharField(max_length=800, help_text="Input option 3", blank=True)
    option4 = models.CharField(max_length=800, help_text="Input option 4", blank=True)
    option5 = models.CharField(max_length=800, help_text="Input option 5", blank=True)
    answer = models.PositiveSmallIntegerField(help_text="Input the option that is the correct answer. eg: '1' for option1 or '2' for option2")
    mark = models.PositiveSmallIntegerField("What is the score/mark of this question?")
    
    def __str__(self):
        return self.detail


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question", help_text="associated question")
    answered_by = models.ForeignKey("UserDetail", on_delete=models.CASCADE, related_name="student", help_text="Student Username")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_answered", help_text="What course does this question belong to?")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text="What level is the answer meant for?")
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="What semester is the answer meant for?")
    user_answer = models.PositiveSmallIntegerField("Choose your answer", blank=True, null=True)
    is_answer = models.BooleanField(help_text="Is the answer correct?", blank=True, default=False)
    date = models.DateTimeField(help_text="When was this examination taken?", auto_now_add=True, editable=False)
    
    def get_question_option(self):
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
        else: return "No answer choosen."


    def get_semester(self):
        return display_semester(self.semester)
    
    def __str__(self):
        return self.get_question_option()
    


class CourseResult(models.Model):
    user = models.ForeignKey("UserDetail", on_delete=models.CASCADE, related_name="course_user", help_text="Student Username")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="user_course", help_text="associated course")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text="What level is this course for?")
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="What semester is this course for?")
    score= models.SmallIntegerField("What is the score?")
    grade = models.CharField(max_length=2, help_text="What is the grade?", blank=True, null=True)
    
    def get_semester(self):
        return display_semester(self.semester)
    
    def __str__(self):
        return str(self.score)



class Result(models.Model):
    user = models.ForeignKey("UserDetail", on_delete=models.CASCADE, related_name="result", help_text="Student Username")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text='What is your level.')
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="What semester has this result?")
    total_score = models.SmallIntegerField("Total score for the semester", blank=True, null=True)
    total_courses = models.PositiveSmallIntegerField("How many courses were offered in total?")
    total_units = models.SmallIntegerField("Total units for the semester", blank=True, null=True)
    gpa = models.FloatField(null=True, help_text="What is the Grade Point Average (GPA)?")
    date = models.DateTimeField(help_text="When was this result computed?", auto_now_add=True, editable=False)
    

    def __str__(self):
        return self.get_semester_display() +": " + str(self.total_score)

    
    def get_courses(self):
        return CourseResult.objects.filter(user=self.user, level=self.level, semester=self.semester)


    def get_semester(self):
        return display_semester(self.semester)



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
    student = models.OneToOneField("UserDetail", on_delete=models.CASCADE, unique=True, help_text='Username of registered student.')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programme", help_text="Your Department", blank=True, null=True)
    programme = models.CharField(max_length=5, choices=PROGRAMMES, blank=True, help_text="Please select your Programme Type.")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text="Please select your current level.")
    reg_no = models.CharField(max_length=30, help_text="Enter your Registration Number.", blank=True)
    jamb_no = models.CharField(max_length=30, help_text="Enter your JAMB Registration Number.", blank=True)
    student_mode = models.CharField(max_length=50, choices=STUDENT_MODES, blank=True, help_text="Student's Mode")
    student_type = models.CharField(max_length=50, choices=STUDENT_TYPES, blank=True, help_text="Student Type")
    entry_mode = models.CharField(max_length=50, choices=ENTRY_MODES, blank=True, help_text="Student's Mode of Entry.")
    study_mode = models.CharField(max_length=50, choices=STUDY_MODES, blank=True, help_text="Student's Mode of Study.")
    entry_year = models.SmallIntegerField("Admission year. (e.g. 2018)", blank=True, null=True)
    graduation_year = models.SmallIntegerField("Graduation year. (e.g. 2022)", blank=True, null=True)

    def __str__(self):
        return self.department or self.student.user.username
    


class Sponsor(models.Model):
    name = models.CharField(max_length=250, help_text="Enter sponsor's full name. Surname first.", blank=True)
    student = models.OneToOneField("UserDetail", on_delete=models.CASCADE, unique=True, help_text='Username of registered student.')
    address = models.CharField(max_length=250, help_text="Sponsor's Address", blank=True)
    phone = models.IntegerField(help_text="Sponsor's Mobile No.", null=True, blank=True)
    relationship = models.CharField(max_length=2, choices=RELATIONSHIPS, blank=True, help_text='How are you related?')
    email = models.EmailField(help_text="Sponsor's Email", blank=True)

    def __str__(self):
        return self.student.user.username



class Kin(models.Model):
    name = models.CharField(max_length=250, help_text="Enter Next of Kin's full name. Surname first.", blank=True)
    student = models.OneToOneField("UserDetail", on_delete=models.CASCADE, unique=True, help_text='Username of registered student.')
    address = models.CharField(max_length=250, help_text="Next of Kin's Address", blank=True)
    phone = models.IntegerField(help_text="Next of Kin's Mobile No.", null=True, blank=True)
    relationship = models.CharField(max_length=2, choices=RELATIONSHIPS, blank=True, help_text='How are you related?')
    email = models.EmailField(help_text="Next of Kin's Email", blank=True)

    def __str__(self):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, help_text='Username of registered user.')
    middle_name = models.CharField(max_length=150, help_text='middle name', blank=True)
    birth_date = models.DateTimeField("Date of birth", null=True, blank=True)
    email = models.EmailField(help_text="Email Address", blank=True)
    gender = models.CharField(max_length=2, choices=GENDERS, blank=True, help_text='Please select your gender')
    status = models.CharField(max_length=2, choices=STATUSES, blank=True, help_text='Please select your relationship status.')
    religion = models.CharField(max_length=2, choices=RELIGIONS, blank=True, help_text='Please select your religion.')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="state", help_text="State of origin", blank=True, null=True)
    lga = models.ForeignKey(LGA, on_delete=models.CASCADE, related_name="lga", help_text="Local Government of origin", blank=True, null=True)
    home_town = models.CharField(max_length=250, help_text="Home Town", blank=True)
    perm_address = models.CharField(max_length=300, help_text="Permanent Address", blank=True)
    phone = models.IntegerField(help_text="Your Mobile Phone Number", null=True, blank=True)
    contact_address = models.CharField(max_length=300, help_text="Contact Address", blank=True)
    blood_group = models.CharField(max_length=10, help_text="Blood Group", blank=True)
    genotype = models.CharField(max_length=10, help_text="Genotype", blank=True)
    signature = models.ImageField(upload_to=u_s_path, blank=True, help_text='Choose your signature.')
    pictures = models.ImageField(upload_to=u_p_path, blank=True, help_text='Choose your profile picture.')
    last_modified = models.DateTimeField('Last modified date', auto_now=True)
    
    
    def __str__(self):
        return self.user.username
    

    def full_name(self):
        return self.user.get_full_name() + self.middle_name + self.user.username
    


class Token(models.Model):
    """This model represents random tokens generated for each course a Student studies. The token is unique to a given user and for a given course.
    It is required for a Student to be able to take part in any and every examination.

    All the fields are required and each field itself is self explanatory."""
    
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name='user_token', help_text='Generate Token for User.')
    token = models.CharField(max_length=250, help_text="Access Token")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text='Generate token for what level?')
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="Generate token for what semester?")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="token_course", help_text="Generate token for what course?")

    class Meta:
        permissions = (
            ("create_token", "Can create token for users"),
            ("flush_token", "Can flush/delete tokens"),
        )
    
    def __str__(self):
        return self.token
    


class UserCourse(models.Model):
    """Courses a Student can study.
    Each course must be registered before the user can study it or atleast take exams and test/assignment on the course.

    All fields are required.
    """

    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, related_name="register_course", help_text="Student registering course")
    level = models.CharField(max_length=3, choices=LEVELS, default=100, help_text="Student's level")
    semester = models.CharField(max_length=2, choices=SEMESTERS, default=1, help_text="Student's semester")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="registered_course", help_text="What course are you registering?")


    def __str__(self):
        return self.course
