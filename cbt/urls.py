from django.urls import path, include

from . import views

urlpatterns = [
    path('test/', views.test, name="test"),


    path('', views.index, name='index'),
    path('faq/', views.faq, name="faq"),
    

    path('u/', include('django.contrib.auth.urls')),
    path('u/register/', views.register, name="register"),
    
    
    path('user/<username>/', views.profile, name="profile"),
    path('user/<username>/<int:t>/edit/', views.edit_profile, name="edit_profile"),
    
    
    path("questions/choose/", views.choose_question, name="choose_question"),
    path("questions/<int:course>/<int:level>/<int:semester>/", views.questions, name="questions"),


    path("questions/new/", views.new_question, name="new_question"),
    path("questions/<int:course>/<int:level>/<int:semester>/<int:total>/", views.add_question, name="add_question"),
    
    
    path("results/semester/", views.show_semester_result, name="show_semester_result"),
    path("results/<username>/<int:level>/<int:semester>/", views.semester_result, name="semester_result"),
    
    path("results/course/", views.show_course_result, name="show_course_result"),
    path("results/<username>/<int:course>/<int:level>/<int:semester>/", views.course_result, name="course_result"),
    
    path("level_result/choose/", views.choose_level_result, name="choose_level_result"),
    path("level_result/<int:level>/", views.level_result, name="level_result"),


    path("mark_answer/", views.mark_answer, name="mark_answer"),
    path("mark_answers/<int:course>/<int:level>/<int:semester>/", views.mark_answers, name="mark_answers"),
    
    
    path("compile_result/", views.compile_result, name="compile_result"),
    path("compiled_results/<int:level>/<int:semester>/", views.compiled_results, name="compiled_results"),


    path("register_course/<username>/", views.register_course, name="register_course"),
    path("register_courses/<username>/<int:level>/<int:semester>/", views.register_courses, name="register_courses"),

    path("registered_course/<username>/", views.registered_course, name="registered_course"),
    path("registered_courses/<username>/<int:level>/<int:semester>/", views.registered_courses, name="registered_courses"),


    path("gen_tokens/<username>/", views.gen_token, name="gen_tokens"),
    path("show_tokens/<username>/", views.show_tokens, name="show_tokens"),
    path("tokens/<username>/<int:level>/<int:semester>/<int:course>/", views.tokens, name="tokens"),

    path("flush_token/<username>/", views.flush_token, name="flush_token"),
    path("flush_tokens/<username>/<int:level>/<int:semester>/<int:course>/", views.flush_tokens, name="flush_tokens"),

    #
]

