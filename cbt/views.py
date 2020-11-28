"""The views for the cbt application.

Defines the needed views for performing varying actions on the website.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import (
    get_list_or_404, get_object_or_404, redirect, render, reverse
)
from django.views.generic import DetailView, FormView, ListView

from cbt.countries import nigeria
from cbt.forms import (
    AddQuestionForm, ChooseCourseForm, CompileResultForm, LevelResultForm,
    GenerateTokenForm, ChooseExamForm
)
from cbt.models import (
    Answer, Course, CourseResult, Question, Result, Token, UserCourse,
)
from permissions import (
    can_add_question, CanAddQuestionMixin, can_take_exam, is_active,
    IsActiveMixin
)
from cbt.tools import (
    add_country, add_locals, add_states, grade, token, validate_token
)


class NewQuestionView(LoginRequiredMixin, CanAddQuestionMixin, FormView):
    """View for choosing which course to add questions to."""

    template_name = "cbt/generic_form.html"
    form_class = AddQuestionForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('add_question', kwargs={
            'course': data['course'].id, 'total': int(data['total'])
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Where To Add Question'
        context['detail_text'] = """Please select the <strong>Course, Level,
            Semester, and Number of Questions(total)</strong> you want to add
            in other to proceed."""
        return context


@login_required
def add_question(request, course, total):
    """View for adding question(s) for selected course."""

    if not can_add_question(request):
        messages.warning(
            request, "You lack the necessary permissions to add question(s)."
        )
        return redirect('index')

    course = get_object_or_404(Course, pk=course)
    question_form_set = modelformset_factory(
        Question, exclude=['course', 'semester', 'level'], extra=total,
        max_num=30
    )
    if request.method == 'POST':
        formset = question_form_set(request.POST)
        if formset.is_valid():
            # Check if any of the question forms was modified.
            if formset.has_changed():
                # Capture the total number of questions
                t_f = formset.total_form_count()
                # Go through all the questions and set necessary fields.
                while t_f:
                    formset[t_f-1].instance.course = course
                    formset[t_f-1].instance.level = course.level
                    formset[t_f-1].instance.semester = course.semester
                    t_f -= 1

                saved = len(formset.save())
                messages.success(
                    request, f'{saved} Questions added successfully.'
                )
                return redirect('index')
            messages.info(
                request, "You didn't change any of the questions form. "
                "Hence, No questions was added."
            )
        else:
            messages.warning(
                request, "Some invalid details discovered. Please correct"
                " accordingly below."
            )

    else:
        formset = question_form_set(queryset=Question.objects.none())

    return render(request, "cbt/add_question.html", {
        "formset": formset, "course": course
    })


class ChooseQuestionView(LoginRequiredMixin, IsActiveMixin, FormView):
    """This view allows the user to choose which examination to take.

    Renders a self explanatory form and all fields are required.

    Redirects to questions view if choices are valid otherwise, returns the
    form with error message(s) for corrections. If the user account is
    inactive, they're redirected to the Home Page."""

    template_name = "cbt/generic_form.html"
    form_class = ChooseExamForm

    def form_valid(self, form):
        """Validate exam Token and other requirements."""
        data = form.cleaned_data
        if validate_token(self.request, data['token'], allow_test=True):
            self.success_url = reverse("questions", kwargs={
                'course': data['course'].id
            })
            return super().form_valid(form)
        messages.warning(
            self.request, "Invalid Token. Please try again. Note: Tokens are "
            "caSE SensITive"
        )
        return redirect('choose_question')

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Examination You Want To Take'
        context['detail_text'] = """To proceed, select the <strong>Course
            </strong> and enter the <strong>Token</strong> for the examination
            you want to take.."""
        return context


@login_required
def questions(request, course):
    """Allows user to seat for selected exam.

    This view allows permitted users to seat for examination. Users without
    necessary permissions are redirected to choose the exam they want to seat
    for."""

    if not can_take_exam(request, course):
        messages.warning(
            request, "Sorry! You don't have the necessary permissions to seat"
            " for this exam."
        )
        return redirect('choose_question')

    ques = get_list_or_404(Question, course=course)
    AnswerFormSet = modelformset_factory(
        Answer, fields="__all__", extra=len(ques), max_num=30
    )
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(
                request, "Answer script submitted succesfully. Wishing you "
                "good luck. You will be communicated when result is released."
            )
            # Invalidate and delete token here to avoid reuse.
            return redirect('index')
        f_q = zip(formset, ques)

    else:
        formset = AnswerFormSet(queryset=Answer.objects.none())
        f_q = zip(formset, ques)

    return render(request, "cbt/questions.html", {
        "formset": formset, "ques": ques, "f_q": f_q
    })


class MarkScriptView(LoginRequiredMixin, CanAddQuestionMixin, FormView):
    """View for choosing which exam script to mark.

    Check that the user is a lecturer and that the account is still active.
    Redirects to Mark Scripts page on success."""

    template_name = "cbt/generic_form.html"
    form_class = ChooseCourseForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('mark_scripts', kwargs={
            'course': data['course'].id
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Exam Scripts To Mark'
        context['detail_text'] = """Please select details of the exam
            script(s) to mark and click <strong class="text-success">Proceed
            </strong>."""
        return context


@login_required
def mark_scripts(request, course):
    """Marks students' answer scripts of the selected course.

    Checks if the user user has necessary permissions.
    Else, returns appropriate message and redirects to Home Page."""

    # Check that user can mark scripts.
    if not can_add_question(request):
        messages.warning(
            request, "You lack the necessary permissions to mark script(s)."
        )
        return redirect('index')

    # Capture the answers from database and create necessary variables.
    answers = get_list_or_404(Answer, course=course)
    score = 0  # Holds total score of all students.
    user_score = {}  # Holds each student and respective total score.

    # Loop through the answers and mark the script of each user.
    for a in answers:
        if a.user_answer == a.question.answer:  # Is user choice correct?
            a.is_answer = True  # Then mark it correct.
            a.save()  # And save.
            score += a.question.score  # Update overall total score.
            # Update user score in the dict.
            if a.answered_by in user_score:
                user_score[a.answered_by] += a.question.score
            # Or add user to dict with corresponding score.
            else:
                user_score[a.answered_by] = a.question.score

    if user_score:
        # Loop through the course results dict.
        for u, v in user_score.items():
            # And create user result for each result marked.
            CourseResult.objects.get_or_create(
                user=u, course=answers[0].course, level=answers[0].level,
                semester=answers[0].semester, score=v, grade=grade(v)
            )

        cr = CourseResult.objects.filter(
            course=answers[0].course, level=answers[0].level,
            semester=answers[0].semester
        )
        return render(request, 'cbt/marked_scripts.html', context={
            'ans': cr[0], 'score': score, 'cr': cr
        })

    messages.info(
        request, "No results were marked. Ensure the students have taken"
        " their exams and try again."
    )
    return redirect('mark_script')


class CompileResultView(LoginRequiredMixin, CanAddQuestionMixin, FormView):
    """View for choosing which semester result to compile.

    Check that the user has necessary permissions (Lecturer) and that account
    is still active.

    Redirects to compile_results view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = CompileResultForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('compile_results', kwargs={
            'level': int(data["level"]), 'semester': int(data["semester"])
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Results To Compile'
        context['detail_text'] = """Please select the <strong>Semester
            </strong> and <strong>Level</strong> you want to compile the
            results and then click <strong class="text-success">Proceed
            </strong>."""
        return context


@login_required
def compile_results(request, level, semester):
    """Compiles selected semester and level results for all students.

    Loops through all the course results and compiles the results for that
    semester and level.

    Renders the result in the template."""

    # Check that user can mark scripts.
    if not can_add_question(request):
        messages.warning(
            request, "You lack necessary permissions to compile results(s)."
        )
        return redirect('index')

    # Get all results for the level and semester.
    results = get_list_or_404(CourseResult, level=level, semester=semester)
    c_rs = {}
    # Compile the results.
    for result in results:
        # If the result has being added, update the record.
        if result.user in c_rs:
            c_rs[result.user][0] += 1
            c_rs[result.user][1] += result.score
            c_rs[result.user][2] += result.course.unit
            c_rs[result.user][3] += result.course.unit * grade(
                result.score, int_grade=True
            )
        # Else, add to record.
        else:
            c_rs[result.user] = [
                1, result.score, result.course.unit, result.course.unit *
                grade(result.score, int_grade=True)
            ]

    # Save compiled results to database
    for k, v in c_rs.items():
        Result.objects.get_or_create(
            user=k, level=level, semester=semester, total_score=v[1],
            total_courses=v[0], total_units=v[2], gpa=v[3]/v[2]
        )

    # Get result for display in template.
    c_results = get_list_or_404(Result, level=level, semester=semester)
    return render(request, 'cbt/compiled_result.html', context={
        'results': c_results, 'level': c_results[0].get_level_display(),
        'semester': c_results[0].get_semester_display()
    })


class ShowSemesterResultView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for choosing which semester result to display.

    Check that the user's account is still active.

    Redirects to semester_result view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = CompileResultForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('semester_result', kwargs={
            'level': int(data["level"]), 'semester': int(data["semester"])
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Semester Result To Display'
        context['detail_text'] = '''Please select the <strong>Semester
            </strong> and <strong>Level</strong> you want to access the
            results and then click <strong class="text-success">Proceed
            </strong>.'''
        return context


class SemesterResultDetail(DetailView):
    """Returns the matched semester result."""

    model = Result
    template_name = "cbt/semester_result.html"
    context_object_name = "result"

    def get_object(self):
        """Looks up the semester result to display and returns it."""
        return get_object_or_404(
            Result, user=self.request.user.userdetail,
            level=self.kwargs.get('level', 0),
            semester=self.kwargs.get('semester', 0)
        )


class ShowLevelResultView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for choosing which level/session result to display.

    Check that the user's account is still active.

    Redirects to level_result view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = LevelResultForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('level_result', kwargs={
            'level': int(data["level"])
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Level Result To Display'
        context['detail_text'] = '''Please select the <strong>Level/Session
            </strong> you want to access the results and then click <strong
            class="text-success">Proceed</strong>.'''
        return context


class LevelResultList(LoginRequiredMixin, IsActiveMixin, ListView):
    """Returns list of matched Level/Session results."""

    model = Result
    template_name = "cbt/level_result.html"
    context_object_name = "results"

    def get_queryset(self):
        """Returns the queryset to work with."""
        return get_list_or_404(
            Result, user=self.request.user.userdetail,
            level=self.kwargs.get('level', 0)
        )

    def get_context_data(self, **kwargs):
        """Return the data used in the template's rendering."""
        context = super().get_context_data(**kwargs)
        context['user_detail'] = self.object_list[0].user
        context['cgpa'] = self.cgpa(self.object_list[0], self.object_list[1])
        context['level'] = self.object_list[0].get_level_display()
        return context

    def cgpa(self, first_result, second_result):
        """Returns the CGPA of two results.

        Given two results, returns the Cumulative Grade Point Average (CGPA)
        of the two results."""
        return (first_result.total_score + second_result.total_score) / (
            first_result.total_units + second_result.total_units)


class ShowCourseResultView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for choosing which course result to display.

    Check that the user's account is still active.

    Redirects to course_result view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = ChooseCourseForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('course_result', kwargs={
            'course': int(data["course"].id)
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Course Result To Display'
        context['detail_text'] = '''Please select the <strong>Course
            </strong> you want to access the result and then click <strong
            class="text-success">Proceed</strong>.'''
        return context


class CourseResultDetail(DetailView):
    """Returns the matched course result."""

    model = CourseResult
    template_name = "cbt/course_result.html"
    context_object_name = "result"

    def get_object(self):
        """Looks up the course result to display and return it."""
        return get_object_or_404(
            CourseResult, user=self.request.user.userdetail,
            course=self.kwargs.get('course', 0),
        )


class RegisterCourseView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for choosing the courses to register.

    Check that the user's account is still active.

    Redirects to register_courses view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = CompileResultForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('register_courses', kwargs={
            'level': int(data["level"]), 'semester': int(data["semester"])
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Where To Register Courses'
        context['detail_text'] = '''Please select the <strong>Level/Session
            </strong> and <strong>Semester </strong> you want to register the
            courses and then click <strong class="text-success">
            Proceed</strong>.'''
        return context


@login_required
def register_courses(request, level: int, semester: int):
    """View for registering courses.

    The template being rendered was highly customized to fit the rendering
    needs.

    On form valid, the selected courses are registered and user redirected to
    registered_courses view."""

    # Check that user can mark scripts.
    if not is_active(request):
        messages.warning(
            request, 'You lack necessary permissions to register course(s).'
        )
        return redirect('index')

    courses = get_list_or_404(Course, level=level, semester=semester)
    CourseFormSet = modelformset_factory(
        UserCourse, fields='__all__', extra=len(courses), max_num=len(courses)
    )
    if request.method == 'POST':
        formset = CourseFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(
                'registered_courses', level=level, semester=semester
            )
        f_c = zip(formset, courses)  # zip Formset and courses

    else:
        formset = CourseFormSet(queryset=UserCourse.objects.none())
        f_c = zip(formset, courses)  # zip Formset and courses

    return render(request, "cbt/courses.html", context={
        'formset': formset, 'courses': courses, 'f_c': f_c,
        'level': courses[0].get_level_display(),
        'semester': courses[0].get_semester_display()
    })


class ShowRegisteredCourseView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for choosing which registered course to display.

    Check that the user's account is still active.

    Redirects to registered_courses view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = CompileResultForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('registered_courses', kwargs={
            'level': int(data["level"]), 'semester': int(data["semester"])
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Registered Courses To Display'
        context['detail_text'] = '''Please select the <strong>Level/Session
            </strong> and <strong>Semester</strong> you want to view the
            registered courses and then click <strong class="text-success">
            Proceed</strong>.'''
        return context


class RegisteredCoursesList(LoginRequiredMixin, IsActiveMixin, ListView):
    """Returns list of matched Level/Session results."""

    model = UserCourse
    template_name = "cbt/registered_courses.html"
    context_object_name = "courses"

    def get_queryset(self):
        """Returns the queryset to work with."""
        return get_list_or_404(
            UserCourse, user=self.request.user.userdetail,
            level=self.kwargs.get('level', 0),
            semester=self.kwargs.get('semester', 0)
        )

    def get_total_units(self, courses=[]):
        """Calculates the total course units.

        If courses is provided, it will be used. Else, self.object_list will
        be used."""
        if not courses:
            courses = self.object_list
        total_units = 0
        for c in courses:
            total_units += c.course.unit
        return total_units

    def get_context_data(self, **kwargs):
        """Return the data used in the template's rendering."""
        context = super().get_context_data(**kwargs)
        context['total_units'] = self.get_total_units()
        context['user_detail'] = self.object_list[0].user
        context['level'] = self.object_list[0].get_level_display()
        context['semester'] = self.object_list[0].get_semester_display()
        return context


@login_required
def gen_token(request):
    """View for generating tokens for examinations.

    Examination tokens will be generated for every user that has registered
    the given course.

    Redirects to tokens view page on form valid."""

    # Check that user can generate examination tokens.
    if not can_add_question(request):
        messages.warning(
            request, 'You lack necessary permissions to generate token(s).'
        )
        return redirect('index')

    if request.method == "POST":
        form = GenerateTokenForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            users = UserCourse.objects.filter(
                level=int(data["level"]), semester=int(data["semester"]),
                course=data["course"]
            )
            for u in users:
                Token.objects.create(
                    user=u.user, token=token(), level=int(data['level']),
                    semester=int(data['semester']), course=data['course']
                )
            messages.success(
                request, 'Examination tokens generated successfully.'
            )
            return redirect(
                'tokens', level=int(data['level']),
                semester=int(data['semester']), course=int(data['course'].id)
            )
    else:
        form = GenerateTokenForm()

    return render(request, 'cbt/generic_form.html', context={
        'form': form, 'title_text': 'Select Course To Generate Tokens For',
        'detail_text': '''Please select the <strong>Level/Session</strong>,
        <strong>Semester</strong> and <strong>Course</strong> you want to
        generate Tokens for and then click <strong class="text-success">
        Proceed</strong>.'''
    })


class ShowTokensView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for choosing course tokens that will be displayed.

    Check that the user's account is still active.

    Redirects to tokens view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = GenerateTokenForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('tokens', kwargs={
            'level': int(data["level"]), 'semester': int(data["semester"]),
            'course': int(data['course'].id)
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Choose Course To View The Tokens'
        context['detail_text'] = '''Please select the <strong>Level/Session
            </strong>, <strong>Semester</strong> and <strong>Course</strong>
            you want to access the generated Tokens and then click
            <strong class="text-success">Proceed</strong>.'''
        return context


@login_required
def tokens(request, level, semester, course):
    """View for retrieving and displaying generated token(s).

    Displays matched course tokens if the user has necessary permissions."""

    if not can_add_question(request):
        messages.warning(
            request, 'You lack necessary permissions to access course tokens'
        )
        return redirect('index')

    u_tokens = get_list_or_404(
        Token, level=level, semester=semester, course=course
    )
    return render(request, 'cbt/token.html', context={
        'u_tokens': u_tokens, 'level': u_tokens[0].get_level_display(),
        'semester': u_tokens[0].get_semester_display()
    })


class ShowFlushTokensView(LoginRequiredMixin, IsActiveMixin, FormView):
    """View for selecting which tokens to Flush/Delete.

    Check that the user's account is still active.

    Redirects to flush_tokens view on form valid."""

    template_name = "cbt/generic_form.html"
    form_class = GenerateTokenForm

    def form_valid(self, form):
        """Compute the success URL and call super.form_valid()"""
        data = form.cleaned_data
        self.success_url = reverse('flush_tokens', kwargs={
            'level': int(data["level"]), 'semester': int(data["semester"]),
            'course': int(data['course'].id)
        })
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return the data used in the templates rendering."""
        context = super().get_context_data(**kwargs)
        context['title_text'] = "Choose Course To Flush It's Tokens"
        context['detail_text'] = '''Please select the <strong>Level/Session
            </strong>, <strong>Semester</strong> and <strong>Course</strong>
            you want to flush/delete the generated Tokens and then click
            <strong class="text-success">Proceed</strong>.'''
        return context


@login_required
def flush_tokens(request, level, semester, course):
    """View for flushing/deleleting selected tokens.

    Checks that the user has necessary permissions and then deletes matched
    course's exam tokens."""

    if not can_add_question(request):
        messages.warning(
            request, 'You lack necessary permissions to flush course tokens.'
        )
        return redirect('index')

    try:
        flushed = 0
        tokens = get_list_or_404(
            Token, level=int(level), semester=int(semester),
            course=int(course)
        )
        course = f"{tokens[0].course.title} ({str(tokens[0].course.code)})"
        for t in tokens:
            t.delete()
            flushed += 1
    except Exception:
        flushed = 0
        course = "Selected Course"

    messages.success(request, f"""
        {flushed} token(s) for <strong>{course}</strong> Flushed/Deleted
        successfully.
    """)
    return redirect('index')


@login_required
def insert_country(request, country):
    """View for adding new country into the database"""

    if country.lower() == "nigeria":
        return HttpResponse(add_country("Nigeria"))
    return HttpResponse("No Country Added.")


@login_required
def insert_states(request, country):
    if country.lower() == "nigeria":
        return HttpResponse(add_states("Nigeria", nigeria.STATES))
    return HttpResponse("No States Added.")


@login_required
def insert_lgas(request, country):
    if country.lower() == "nigeria":
        return HttpResponse(add_locals("Nigeria", nigeria.LOCALS))
    return HttpResponse("No LGA/Province added.")
