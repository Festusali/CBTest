from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .models import UserDetail, Kin, Sponsor, Question, Answer, CourseResult, Result, Course, Programme, UserCourse, Token

from .models import display_level, display_semester
from .forms import RegisterUserForm, EditUserDetailForm, EditKinForm, EditSponsorForm, AddQuestionForm, ChooseQuestionForm, CompileResultForm, EditProgrammeForm, LevelResultForm, GenerateTokenForm, RegisterCourseForm, ChooseExamForm

from .tools import can_add_question, can_modify, can_like, grade, token


# Create your views here.
def index(request):
    return render(request, "cbt/index.html")


def faq(request):
    return render(request, "cbt/faq.html")



@login_required
def edit_profile(request, username, t):
    user_detail = UserDetail.objects.get(user=username)
    if not can_modify(request, user_detail.user.username):
        return render(request, "cbt/edit_profile.html", {"perm": False, "t": t})
    if t == 1:
        form = EditUserDetailForm(instance=user_detail)
    elif t == 2:
        sponsor = Sponsor.objects.get(student=user_detail)
        form = EditSponsorForm(instance=sponsor)
    elif t == 3:
        kin = Kin.objects.get(student=user_detail)
        form = EditKinForm(instance=kin)
    elif t == 4:
        programme = Programme.objects.get(student=user_detail)
        form = EditProgrammeForm(instance=programme)
    else: form = "" #to avoid error.

    if request.method == "POST":
        if t == 1:
            form = EditUserDetailForm(request.POST, request.FILES, instance=user_detail)
        elif t == 2:
            form = EditSponsorForm(request.POST, instance=sponsor)
        elif t == 3:
            form = EditKinForm(request.POST, instance=kin)
        elif t == 4:
            form = EditProgrammeForm(request.POST, instance=programme)
            
        if form.is_valid():
            form.save()
            return redirect("profile", username=user_detail.user.id)
        return render(request, "cbt/edit_profile.html", {"form": form, "t": t})
    
    return render(request, "cbt/edit_profile.html", {"form": form, "t": t})
    


@login_required
def profile(request, username):
    user = UserDetail.objects.get(user=username)
    if not can_modify(request, user.user.username):
        return render(request, "cbt/profile.html", {"perm": False})
    kin = Kin.objects.get(student=user)
    sponsor = Sponsor.objects.get(student=user)
    programme = Programme.objects.get(student=user)
    return render(request, "cbt/profile.html", {"user": user, "kin": kin, "sponsor": sponsor, "programme": programme, }, )



def register(request):
    #If POST request method.
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid(): #Is form valid?
            new_user = User.objects.create_user(username=form.cleaned_data["username"], email=form.cleaned_data["email"], password=form.cleaned_data["password"])
            print(form.cleaned_data, new_user)
            try: 
                user_detail = UserDetail.objects.create(user=new_user, email=new_user.email, phone=0)
                Kin.objects.create(student=user_detail)
                Sponsor.objects.create(student=user_detail)
                Programme.objects.create(student=user_detail)
            except:
                print(new_user)
                new_user.delete()
                return render(request, "cbt/register.html", {"form": form})
            return redirect("profile", username=new_user.id)    
    else:
        form = RegisterUserForm() #Create empty user form
    return render(request, "cbt/register.html", {"form": form})
        

@login_required
def new_question(request):
    form = AddQuestionForm()
    if can_add_question(request) and request.method == "POST":
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("add_question", course=data["course"].id, level=int(data["level"]), semester=int(data["semester"]), total=int(data["total"]))
        return render(request, "cbt/choose.html", {"form": form, "add_question": True} )
    
    elif can_add_question(request):
        return render(request, "cbt/choose.html", {"form": form, "add_question": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


@login_required
def add_question(request, course, level, semester, total):
    def get_initials():
        t = total
        initial = []
        i = {"course": course, "level": level, "semester": semester}
        while t:
            initial.append(i)
            t -= 1
        return initial
    
    def get_details():
        c = Course.objects.get(pk=course).title
        l = display_level(level)
        s = display_semester(semester)
        return {"course": c, "level": l, "semester": s}

    if not can_add_question(request):
        return render(request, "cbt/add_question.html", {"perm": False})

    QuestionFormSet = modelformset_factory(Question, fields="__all__", extra=total, max_num=30)
    if request.method == 'POST':
        formset = QuestionFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponse("Question added.")
        return render(request, "cbt/add_question.html", {"formset": formset, "can_add": True, "total": total, "details": get_details(), })
    
    formset = QuestionFormSet(queryset=Answer.objects.none(), initial=get_initials())
    return render(request, "cbt/add_question.html", {"formset": formset, "can_add": True, "total": total, "details": get_details(), })



@login_required
def choose_question(request):
    """This view allows the user to choose which examination to take.

    The return form is self explannatory and all fields are required.

    Redirects to questions view if choices are valid otherwise, returns the form with error message(s) for corrections. If the user don't have permissions to take exams, the appropriate view is returned with permission denied warning."""

    if not can_like(request):
        return render(request, "cbt/choose.html", {"perm": False})
    form = ChooseExamForm()
    if request.method == "POST":
        form = ChooseExamForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = UserDetail.objects.get(user=request.user)
                token = Token.objects.get(user=user, token=data["token"], course=data["course"])
                return redirect("questions", course=token.course.id, level=token.level, semester=token.semester, )
            except:
                return render(request, "cbt/choose.html", {"form": form, "exam": True, "inv_tok": True, }, )
        return render(request, "cbt/choose.html", {"form": form, "exam": True} )
    
    return render(request, "cbt/choose.html", {"form": form, "exam": True} )


@login_required
def questions(request, course, level, semester):
    if not can_like(request):
        return render(request, "cbt/choose.html", {"perm": False})
    
    ques = Question.objects.filter(course=course, level=level, semester=semester)
    AnswerFormSet = modelformset_factory(Answer, fields="__all__", extra=len(ques), max_num=30)
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponse("Thank you for taking the exam. We wish you the best of luck.")
        f_q = zip(formset, ques)
        return render(request, "cbt/questions.html", {"formset": formset, "ques": ques, "f_q": f_q, "semester": semester, })

    else:
        formset = AnswerFormSet(queryset=Answer.objects.none())
        f_q = zip(formset, ques)
        return render(request, "cbt/questions.html", {"formset": formset, "ques": ques, "f_q": f_q, "semester": semester, })
    
    return render(request, "cbt/questions.html", {"ques": ques, "semester": semester, })



@login_required
def mark_answer(request):
    form = ChooseQuestionForm()
    if can_add_question(request) and request.method == "POST":
        form = ChooseQuestionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("mark_answers", course=data["course"].id, level=int(data["level"]), semester=int(data["semester"]), )
        return render(request, "cbt/choose.html", {"form": form, "mark": True} )
    
    elif can_add_question(request):
        return render(request, "cbt/choose.html", {"form": form, "mark": True} )

    else: return render(request, "cbt/choose.html", {'perm': False} )



@login_required
def mark_answers(request, course, level, semester):
    if not can_add_question(request):
        return render(request, "cbt/choose.html", {"perm": False})
    answers = Answer.objects.filter(course=course, level=level, semester=semester)
    score = 0
    user_score = {}
    for a in answers:
        if a.user_answer == a.question.answer:
            a.is_answer = True
            a.save()
            score += a.question.mark
            if a.answered_by in user_score:
                user_score[a.answered_by] += a.question.mark
            else:
                user_score[a.answered_by] = a.question.mark
    
    if user_score:
        for u, v in user_score.items():
            CourseResult.objects.get_or_create(user=u, course=answers[0].course, level=level, semester=semester, score=v, grade=grade(v))
        
        cr = CourseResult.objects.filter(course=answers[0].course, level=level, semester=semester)
        return render(request, "cbt/mark_answers.html", {"ans": cr[0], "score": score, "cr": cr })
    
    return HttpResponse("No results were marked.")



@login_required
def compile_result(request):
    form = CompileResultForm()
    if can_add_question(request) and request.method == "POST":
        form = CompileResultForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("compiled_results", level=int(data["level"]), semester=int(data["semester"]), )
        return render(request, "cbt/choose.html", {"form": form, "compile": True} )
    
    elif can_add_question(request):
        return render(request, "cbt/choose.html", {"form": form, "compile": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


@login_required
def compiled_results(request, level, semester):
    results = CourseResult.objects.filter(level=level, semester=semester)
    
    if not can_add_question(request):
        return render(request, "cbt/display_result.html", {"perm": False} )

    c_rs = {}
    for result in results:
        if result.user in c_rs:
            c_rs[result.user][0] += 1
            c_rs[result.user][1] += result.score
            c_rs[result.user][2] += result.course.unit
            c_rs[result.user][3] += result.course.unit * grade(result.score, int_grade=True)
            
        else:
            c_rs[result.user] = [1, result.score, result.course.unit, result.course.unit * grade(result.score, int_grade=True)]
            
    for k, v in c_rs.items():
        Result.objects.get_or_create(user=k, level=level, semester=semester, total_score=v[1], total_courses=v[0], total_units=v[2], gpa=v[3]/v[2])
    
    c_results = Result.objects.filter(level=level, semester=semester)
    return render(request, "cbt/display_result.html", {"results": c_results, "level": display_level(level), "semester": display_semester(semester), "compile": True, })




@login_required
def show_semester_result(request):
    form = CompileResultForm()
    if can_like(request) and request.method == "POST":
        form = CompileResultForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("semester_result", username=request.user.id, level=int(data["level"]), semester=int(data["semester"]), )
        return render(request, "cbt/choose.html", {"form": form, "sem_result": True} )
    
    elif can_like(request):
        return render(request, "cbt/choose.html", {"form": form, "sem_result": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


@login_required
def semester_result(request, username, level, semester):
    user = UserDetail.objects.get(user=username)
    if not can_modify(request, user.user.username):
        return render(request, "cbt/display_result.html", {"perm": False} )
    
    result = Result.objects.get(user=username, level=level, semester=semester)
    courses = result.get_courses()
    if result:
        return render(request, "cbt/display_result.html", {"user_detail": user, "result": result, "courses": courses, "level": display_level(level), "semester": display_semester(semester), "s_result": True, })
    
    return render(request, "cbt/choose.html", {"perm": False} )



@login_required
def choose_level_result(request):
    form = LevelResultForm()
    if can_like(request) and request.method == "POST":
        form = LevelResultForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("level_result", level=int(data["level"]), )
        return render(request, "cbt/choose.html", {"form": form, "lev_result": True} )
    
    elif can_like(request):
        return render(request, "cbt/choose.html", {"form": form, "lev_result": True} )

    else: return render(request, "cbt/choose.html", {"perm": True} )


@login_required
def level_result(request, level):
    user = UserDetail.objects.get(user=request.user)
    if not can_modify(request, user.user.username):
        return render(request, "cbt/display_result.html", {"perm": False} )
    
    result1 = Result.objects.get(user=user.user, level=level, semester=1)
    result2 = Result.objects.get(user=user.user, level=level, semester=2)
    results = zip(result1.get_courses(), result2.get_courses())
    cgpa = (result1.total_score + result2.total_score) / (result1.total_units + result2.total_units)
    if results:
        return render(request, "cbt/display_result.html", {"user_detail": user, "results": results, "result1": result1, "result2": result2, "cgpa": cgpa, "level": display_level(level), "l_result": True, })
    
    return render(request, "cbt/choose.html", {"perm": False} )
    


@login_required
def show_course_result(request):
    form = ChooseQuestionForm()
    if can_like(request) and request.method == "POST":
        form = ChooseQuestionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("course_result", username=request.user.id, course=data["course"].id, level=int(data["level"]), semester=int(data["semester"]), )
        return render(request, "cbt/choose.html", {"form": form, "cou_result": True} )
    
    elif can_like(request):
        return render(request, "cbt/choose.html", {"form": form, "cou_result": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


@login_required
def course_result(request, username, course, level, semester):
    result = CourseResult.objects.get(user=username, level=level, semester=semester, course=course)
    if not can_modify(request, result.user.username):
        return render(request, "cbt/display_result.html", {"perm": False} )
    elif result:
        return render(request, "cbt/display_result.html", {"result": result, "c_result": True, })
    return render(request, "cbt/choose.html", {"perm": False} )



@login_required
def register_course(request, username):
    form = CompileResultForm()
    if can_like(request) and request.method == "POST":
        form = CompileResultForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("register_courses", username=int(username), level=int(data["level"]), semester=int(data["semester"]), )
        return render(request, "cbt/choose.html", {"form": form, "reg_course": True} )
    
    elif can_like(request):
        return render(request, "cbt/choose.html", {"form": form, "reg_course": True} )

    else: return render(request, "cbt/choose.html", {"perm": True} )


@login_required
def register_courses(request, username, level, semester):
    courses = Course.objects.filter(level=level, semester=semester)
    CourseFormSet = modelformset_factory(UserCourse, fields="__all__", extra=len(courses), max_num=len(courses))
    if request.method == 'POST':
        formset = CourseFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("registered_courses", username=request.user.id, level=level, semester=semester, )
        f_c = zip(formset, courses) # Formset and courses
        return render(request, "cbt/courses.html", {"formset": formset, "courses": courses, "f_c": f_c, "semester": display_semester(semester), "level": display_level(level), })

    else:
        formset = CourseFormSet(queryset=UserCourse.objects.none())
        f_c = zip(formset, courses) # Formset and courses
        return render(request, "cbt/courses.html", {"formset": formset, "courses": courses, "f_c": f_c, "semester": display_semester(semester), "level": display_level(level), })
    
    return render(request, "cbt/questions.html", {"courses": courses, "semester": display_semester(semester), "level": display_level(level), })


@login_required
def registered_course(request, username):
    form = CompileResultForm()
    if can_like(request) and request.method == "POST":
        form = CompileResultForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("registered_courses", username=int(username), level=int(data["level"]), semester=int(data["semester"]), )
        return render(request, "cbt/choose.html", {"form": form, "course_reg": True} )
    
    elif can_like(request):
        return render(request, "cbt/choose.html", {"form": form, "course_reg": True} )

    else: return render(request, "cbt/choose.html", {"perm": True} )


@login_required
def registered_courses(request, username, level, semester):
    courses = UserCourse.objects.filter(user=int(username), level=level, semester=semester)
    if not can_modify(request, courses[0].user.user.username):
        return render(request, "cbt/choose.html", {"perm": False} )
    elif courses:
        total_units = 0
        for c in courses:
            total_units += c.course.unit
        return render(request, "cbt/reg_courses.html", {"courses": courses, "total_units": total_units })
    return render(request, "cbt/choose.html", {"perm": False} )




@login_required
def gen_token(request, username=0):
    """View for generating tokens for examinations.

    If username == 0 (i.e False), tokens will be generated for every user that has registered the given course. Else, generate token only for the given username.

    Returns the generated token(s)."""
    
    form = GenerateTokenForm()
    if can_add_question(request) and request.method == "POST":
        form = GenerateTokenForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if int(username):
                user = UserDetail.objects.get(pk=int(username))
                u_token = Token.objects.create(user=user, token = token(), level=int(data["level"]), semester=int(data["semester"]), course=data["course"], )
                return redirect("tokens", username=u_token.user.id, level=u_token.level, semester=u_token.semester, course=u_token.course.id, )
            else:
                users = UserCourse.objects.filter(level=int(data["level"]), semester=int(data["semester"]), course=data["course"])
                u_token = []
                for u in users:
                    u_token.append(
                        Token.objects.create(user=u.user, token = token(), level=int(data["level"]), semester=int(data["semester"]), course=data["course"], )
                    )
                return redirect("tokens", username=int(username), level=int(data["level"]), semester=int(data["semester"]), course=int(data["course"].id), )

        return render(request, "cbt/choose.html", {"form": form, "gen_token": True} )
    
    elif can_add_question(request):
        return render(request, "cbt/choose.html", {"form": form, "gen_token": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


@login_required
def show_tokens(request, username=0):
    """View for choosing the tokens that will be displayed."""

    form = GenerateTokenForm()
    if can_add_question(request) and request.method == "POST":
        form = GenerateTokenForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("tokens", username=int(username), level=int(data["level"]), semester=int(data["semester"]), course=int(data["course"].id), )
        return render(request, "cbt/choose.html", {"form": form, "s_token": True, } )
    
    elif can_add_question(request):
        return render(request, "cbt/choose.html", {"form": form, "s_token": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


@login_required
def tokens(request, username, level, semester, course):
    """View for retrieving and displaying token(s) already generated for a given course.

    All the parameters are required.

    If username == 0 (i.e False), the tokens for all Students that registered the course will be returned. Else, the token for only the given username will be returned.

    Returns token(s) found."""
    
    if can_add_question(request):
        if int(username):
            user = UserDetail.objects.get(pk=int(username))
            u_token = Token.objects.get(user=user, course=course)
            return render(request, "cbt/token.html", {"u_token": u_token, "level": display_level(level), "semester": display_semester(semester),} )
        else:
            u_tokens = Token.objects.filter(level=level, semester=semester, course=course)
            return render(request, "cbt/token.html", {"u_tokens": u_tokens, "level": display_level(level), "semester": display_semester(semester),} )
    
    else:
        return render(request, "cbt/token.html", {"perm": True, })


@login_required
def flush_token(request, username=0):
    """View for selecting which tokens to Flush/Delete.
    
    If username (i.e username==True), the view redirects with user id in order to delete only selected user's token based on the course, level and semester selected.
    Else, all the students' token for the selected course will be flushed."""

    form = GenerateTokenForm()
    if can_add_question(request) and request.method == "POST":
        form = GenerateTokenForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return redirect("flush_tokens", username=int(username), level=int(data["level"]), semester=int(data["semester"]), course=data["course"].id, )
        return render(request, "cbt/choose.html", {"form": form, "f_token": True, } )
    
    elif can_add_question(request):
        return render(request, "cbt/choose.html", {"form": form, "f_token": True} )

    else: return render(request, "cbt/choose.html", {"perm": False} )


def flush_tokens(request, username, level, semester, course):
    """View for flushing/deleleting selected tokens.
    
    If username (i.e username==True), only the Student's Token is deleted based on the course selected.
    Else, all student's tokens for the selected course will be flushed."""
    
    if can_add_question(request):
        try:
            if int(username):
                user = UserDetail.objects.get(user=request.user)
                tokens = Token.objects.get(user=user, course=int(course))
                flushed = 1
                course = tokens.course.title +" ("+ str(tokens.course.code) +") "
                tokens.delete()
            else:
                flushed = 0
                tokens = Token.objects.filter(level=int(level), semester=int(semester), course=int(course))
                course = tokens[0].course.title +" ("+ str(tokens[0].course.code) +") "
                for t in tokens:
                    t.delete()
                    flushed += 1
        except:
            flushed = 0
            course = "Selected Course"
        return render(request, "cbt/token.html", {"flushed": flushed, "flush": True, "level": display_level(level), "semester": display_semester(semester), "course": course, }, )
    else:
        return render(request, "cbt/choose.html", {"perm": False} )




def test(request):
    """View for testing snippets. Should be deleted before luanching to production server."""
    request.my_variable = "I added this."
    return render(request, "cbt/index.html", {})

