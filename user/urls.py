"""Define URL patterns for the users and related profiles."""


from django.urls import path
from user import views


urlpatterns = [
    path(
        'register/', views.CreateAccountView.as_view(), name='register'
    ),
    path(
        '<int:pk>/<username>/', views.ProfileView.as_view(), name='profile'
    ),
    path(
        '<int:pk>/<username>/edit/', views.edit_biodata, name='edit_profile'
    ),
]
