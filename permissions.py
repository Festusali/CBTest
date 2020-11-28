"""Defines permissions used across the project."""

from django.contrib.auth.mixins import UserPassesTestMixin

from cbt.models import UserCourse
from cbt.tools import validate_token


class IsOwnerMixin(UserPassesTestMixin):
    """Returns True if request.user matches self.get_object().user."""

    permission_denied_message = \
        "You don't have necessary permissions to access this"

    def test_func(self):
        """Determines if the test passes."""
        if self.request.user.is_superuser and self.request.user.is_active:
            return True
        else:
            return (
                self.request.user == self.get_object().user and
                self.request.user.is_active
            )


def is_owner(request, user_detail):
    """A function based equivalent of ISOwnerMixin."""

    if request.user.is_superuser and request.user.is_active:
        return True
    else:
        return request.user == user_detail.user


class CanAddQuestionMixin(UserPassesTestMixin):
    """Check if the current user has permission to create question."""

    permission_denied_message = \
        "You don't have permissions to add question(s)."

    def test_func(self):
        """Return True if the test passes. Else, False."""
        if self.request.user.is_superuser and self.request.user.is_active:
            return True
        else:
            return (
                self.request.user.is_active and
                self.request.user.account_mode == 'L'
            )


def can_add_question(request):
    """A function equalvalent of CanAddQuestionMixin.

    Checks if current user has permission to add question(s)."""

    if request.user.is_superuser and request.user.is_active:
        return True
    else:
        return (
            request.user.is_active and request.user.account_mode == 'L'
        )


'''class CanTakeExamMixin(UserPassesTestMixin):
    """Validates that the user has necessary permissions to take exams.

    Currently, it checks that the user registered for the course. In the
    future, we could check if the user paid the School (Tuition) Fees too."""

    permission_denied_message = \
        "You don't have permissions to seat for this exam."

    def test_func(self):
        """Return True if the test passes. Else, False."""
        if self.request.user.is_superuser and self.request.user.is_active:
            return True
        try:
            registered = UserCourse.objects.get(
                pk=course, user=request.user.userdetail
            )
            if registered and request.user.is_active:
                return True
        except UserCourse.DoesNotExist:
            return False
        return False'''


def can_take_exam(request, course):
    """Validates that the user has necessary permissions to take exams.

    Currently, it checks that the user registered for the course. In the
    future, we could check if the user paid the School (Tuition) Fees too."""

    if request.user.is_superuser and request.user.is_active:
        return True
    # Retrieve the course if user registered for it.
    # Validate the token retrieved from request.session.
    # try:
    registered = UserCourse.objects.get(
        course__pk=course, user=request.user.userdetail
    )
    token = validate_token(
        request, request.session['token'], allow_test=True
    )
    if registered and token and request.user.is_active:
        return True
    '''except (KeyError, UserCourse.DoesNotExist):
        return False
    return False'''


class IsActiveMixin(UserPassesTestMixin):
    """Check if the current user's account is active.

    Later, this mixin may check if user is on widthdrawal and return false.
    Or that the institution suspended the user temporarily."""

    permission_denied_message = \
        "Your account is inactive. Please contact Admin/HoD for assistance."

    def test_func(self):
        """Return True if the test passes. Else, False."""
        return self.request.user.is_active


def is_active(request):
    """Check if the current user's account is active.

    Later, this function may check if user is on widthdrawal and return false.
    Or that the institution suspended the user temporarily."""
    return request.user.is_active
