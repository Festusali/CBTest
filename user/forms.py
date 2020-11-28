# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from user.models import UserModel
from cbt.models import Kin, Programme, Sponsor, UserDetail


class CreateUserForm(UserCreationForm):
    """Extends UserCreationForm to enable caSe-InseSiTiVe validation of
    username"""

    def clean(self):
        """Perform custom form validation."""
        cleaned_data = super(CreateUserForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if UserModel.objects.filter(username__iexact=username).exists():
            self.add_error(
                'username', _('A user with that username already exists.')
            )
        if UserModel.objects.filter(email__iexact=email).exists():
            self.add_error('email', _('''Email address already in use.'''))

        return cleaned_data

    class Meta:
        model = UserModel
        fields = ["username", "email"]


class ChangeUserForm(UserChangeForm):
    """Ensure that the correct model is used for changing user details"""

    class Meta:
        model = UserModel
        fields = ["username", "email"]


class EditUserForm(ModelForm):
    """Form for editing core user details."""

    class Meta:
        model = UserModel
        fields = ["first_name", "last_name"]


class EditUserDetailForm(ModelForm):
    """Form for editing personal user details."""

    class Meta:
        model = UserDetail
        exclude = ["user", "last_modified"]


class EditKinForm(ModelForm):
    """Form for edting Next Of Kin's details."""

    class Meta:
        model = Kin
        exclude = ["student"]


class EditSponsorForm(ModelForm):
    """Form for editing Sponsor's details."""

    class Meta:
        model = Sponsor
        exclude = ["student"]


class EditProgrammeForm(ModelForm):
    """Form for editing Student's Programme details."""

    class Meta:
        model = Programme
        exclude = ["student"]
