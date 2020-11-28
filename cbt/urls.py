"""The URL patterns for the cbt application.
"""

from django.urls import path
from django.views.generic import TemplateView

from cbt import views

urlpatterns = [
    path(
        #  The home page URL.
        '', TemplateView.as_view(template_name='cbt/index.html'), name='index'
    ),
    path(
        #  The Frequently Asked Questions URL.
        'faq/', TemplateView.as_view(template_name='cbt/faq.html'), name='faq'
    ),

    path(
        'questions/choose/', views.ChooseQuestionView.as_view(),
        name='choose_question'
    ),
    path(
        'questions/<int:course>/', views.questions,
        name='questions'
    ),

    path(
        #  The URL to choose which course to add questions to.
        'questions/new/', views.NewQuestionView.as_view(), name='new_question'
    ),
    path(
        #  The URL where you can add questions to selected course.
        'questions/<int:course>/<int:total>/', views.add_question,
        name='add_question'
    ),

    path(
        #  The URL to choose which semester result to view.
        'results/semester/', views.ShowSemesterResultView.as_view(),
        name='show_semester_result'
    ),
    path(
        #  The URL to view selected semester results.
        'results//<int:level>/<int:semester>/',
        views.SemesterResultDetail.as_view(), name='semester_result'
    ),

    path(
        #  The URL to choose which course result to view.
        'results/course/', views.ShowCourseResultView.as_view(),
        name='show_course_result'
    ),
    path(
        #  The URL to view selected course result.
        'results/<int:course>/',
        views.CourseResultDetail.as_view(), name='course_result'
    ),

    path(
        #  The URL to choose which level/session result to view.
        'level_result/choose/', views.ShowLevelResultView.as_view(),
        name='choose_level_result'
    ),
    path(
        #  The URL to view selected level/session results.
        'level_result/<int:level>/', views.LevelResultList.as_view(),
        name='level_result'
    ),

    #  The URL to choose which answer script to mark.
    path('mark_script/', views.MarkScriptView.as_view(), name='mark_script'),
    path(
        #  The view to mark selected script.
        'mark_scripts/<int:course>/', views.mark_scripts, name='mark_scripts'
    ),

    path(
        #  The view to choose which results to compile.
        'compile_result/', views.CompileResultView.as_view(),
        name='compile_result'
    ),
    path(
        #  The view to mark selected results.
        'compile_results/<int:level>/<int:semester>/', views.compile_results,
        name='compile_results'
    ),

    path(
        #  The view to choose which courses to register.
        'register_course/', views.RegisterCourseView.as_view(),
        name='register_course'
    ),
    path(
        # View for registering selected courses.
        'register_courses/<int:level>/<int:semester>/',
        views.register_courses, name='register_courses'
    ),

    path(
        # View for choosing which registered course to display.
        'registered_course/', views.ShowRegisteredCourseView.as_view(),
        name='registered_course'
    ),
    path(
        # View for displaying selected registered courses.
        'registered_courses/<int:level>/<int:semester>/',
        views.RegisteredCoursesList.as_view(), name='registered_courses'
    ),

    # The URL for generating examination tokens.
    path('gen_tokens/', views.gen_token, name='gen_tokens'),
    # The URL for choosing course tokens that will be displayed.
    path('show_tokens/', views.ShowTokensView.as_view(), name='show_tokens'),
    path(
        # The URL for displaying selected course tokens.
        'tokens/<int:level>/<int:semester>/<int:course>/',
        views.tokens, name='tokens'
    ),

    path(
        # The URL to choose which course tokens to flush/delete.
        'flush_token/', views.ShowFlushTokensView.as_view(), name='flush_token'
    ),
    path(
        # The URL for flushing/deleting selected course tokens.
        'flush_tokens/<int:level>/<int:semester>/<int:course>/',
        views.flush_tokens, name='flush_tokens'
    ),

    # Paths for adding countries, states, and lgas
    # Should be removed when django countries package is installed.
    path(
        'insert_country/<country>', views.insert_country,
        name='insert_country'
    ),
    path(
        'insert_states/<country>', views.insert_states, name='insert_states'
    ),
    path('insert_lgas/<country>', views.insert_lgas, name='insert_lgas'),
]
