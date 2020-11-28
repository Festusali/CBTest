"""User model for modelling registered users.

Currently, provides the ability to register and look up users while matching
any character case (upper, lower, title, etc) as against Django's default."""


from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserModelManager(UserManager):
    """Extends UserManager to ensure that CaSe InsenSItiVE usernames are
    recognized as one."""

    def get_by_natural_key(self, username):
        """Enable caSe InsEnSiTive username look up."""
        anycase_username_field = f'{self.model.USERNAME_FIELD}__iexact'
        return self.get(**{anycase_username_field: username})


class UserModel(AbstractUser):
    """Assign UserModelManager as the default object manager."""

    ACCOUNT_MODES = (
        ('S', 'Student'),
        ('L', 'Lecturer'),
        ('D', 'Dean'),
    )

    account_mode = models.CharField(
        max_length=2, choices=ACCOUNT_MODES, blank=True,
        help_text='User account mode'
    )

    objects = UserModelManager()
