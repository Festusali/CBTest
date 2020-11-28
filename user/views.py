from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, DetailView

from cbt.models import UserDetail
from permissions import is_owner, IsOwnerMixin
from user.forms import (
    CreateUserForm, EditKinForm, EditProgrammeForm, EditSponsorForm,
    EditUserDetailForm, EditUserForm
)


class CreateAccountView(SuccessMessageMixin, CreateView):
    """View for creating user accounts."""

    template_name = "user/register.html"
    form_class = CreateUserForm
    success_message = "Account successfully created."
    success_url = settings.LOGIN_URL


class ProfileView(IsOwnerMixin, DetailView):
    """Returns user details. Including Kin, Programme, etc details."""

    model = UserDetail
    template_name = "user/profile.html"
    context_object_name = "user_detail"

    def get_object(self):
        """Returns the object matching the pk and username in URL."""
        return self.get_queryset().select_related().get(
            pk=self.kwargs.get('pk'),
            user__username=self.kwargs.get('username')
        )


'''
class EditBiodataView(View):
    """View for modifying user data. Including, Kin, Sponsor and Programme."""

    kin_form_class = EditKinForm
    programme_form_class = EditProgrammeForm
    sponsor_form_class = EditSponsorForm
    user_detail_form_class = EditUserDetailForm
    template_name = "user/edit_profile.html"
    user_data = None

    """def user_data(self):
        "" "Returns the user data that will be worked on"" "

        return self.get_queryset().get(
            pk=self.kwargs.get('pk'), username=self.kwargs.get('username'),
        )"""

    def get(self, request):
        """Render the forms with correct initial object instances."""

        kin_form = self.kin_form_class(instance=self.user_data)
        programme_form = self.programme_form_class(instance=self.user_data)
        sponsor_form = self.sponsor_form_class(instance=self.user_data)
        user_detail_form = self.user_detail_form_class(
            instance=self.user_data
        )
        return render(request, self.template_name, context={
            'kin_form': kin_form, 'programme_form': programme_form,
            'sponsor_form': sponsor_form,
            'user_detail_form': user_detail_form,
        })

    def post(self, request):
        """Validate the forms and save accordingly if valid."""

        kin_form = self.kin_form_class(request.POST)
        programme_form = self.programme_form_class(request.POST)
        sponsor_form = self.sponsor_form_class(request.POST)
        user_detail_form = self.user_detail_form_class(request.POST)

        if (
            kin_form.is_valid() and programme_form.is_valid() and
            sponsor_form.is_valid() and user_detail_form.is_valid()
        ):  # Check that all forms are valid.
            kin_form.save()
            programme_form.save()
            sponsor_form.save()
            user = user_detail_form.save()
            return redirect(
                reverse_lazy('profile', kwargs={
                    'pk': user.user.id, 'username': user.user.username
                })
            )

        #  The is an invalid form. Render the forms again.
        return render(request, self.template_name, context={
            'kin_form': kin_form, 'programme_form': programme_form,
            'sponsor_form': sponsor_form,
            'user_detail_form': user_detail_form,
        })
'''


def edit_biodata(request, pk, username):
    """Modify user details. Including Kin, Sponsor and Programme details."""

    user_detail = get_object_or_404(UserDetail, pk=pk, user__username=username)
    if not is_owner(request, user_detail):
        return redirect('index')

    if request.method == 'POST':
        kin_form = EditKinForm(request.POST, instance=user_detail.kin)
        programme_form = EditProgrammeForm(
            request.POST, instance=user_detail.programme
        )
        sponsor_form = EditSponsorForm(
            request.POST, instance=user_detail.sponsor
        )
        user_detail_form = EditUserDetailForm(
            request.POST, request.FILES, instance=user_detail
        )
        user_form = EditUserForm(request.POST, instance=user_detail.user)

        if (
            kin_form.is_valid() and programme_form.is_valid() and
            sponsor_form.is_valid() and user_detail_form.is_valid() and
            user_form.is_valid()
        ):  # Check that all forms are valid.
            kin_form.save()
            programme_form.save()
            sponsor_form.save()
            user_detail_form.save()
            user_form.save()
            return redirect(
                'profile', user_detail.pk, user_detail.user.username
            )
        return render(request, 'user/edit_profile.html', context={
            'kin_form': kin_form, 'programme_form': programme_form,
            'sponsor_form': sponsor_form, 'user_form': user_form,
            'user_detail_form': user_detail_form, 'user_detail': user_detail
        })

    kin_form = EditKinForm(instance=user_detail.kin)
    programme_form = EditProgrammeForm(instance=user_detail.programme)
    sponsor_form = EditSponsorForm(instance=user_detail.sponsor)
    user_detail_form = EditUserDetailForm(instance=user_detail)
    user_form = EditUserForm(instance=user_detail.user)
    return render(request, 'user/edit_profile.html', context={
        'kin_form': kin_form, 'programme_form': programme_form,
        'sponsor_form': sponsor_form, 'user_detail_form': user_detail_form,
        'user_detail': user_detail, 'user_form': user_form
    })
