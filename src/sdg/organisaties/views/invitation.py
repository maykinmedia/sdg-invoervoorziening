from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, FormView
from django.views.generic.detail import SingleObjectMixin

from sdg.accounts.forms import InvitationAcceptForm, RoleInlineFormSet
from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.accounts.models import UserInvitation
from sdg.organisaties.models import LokaleOverheid

User = get_user_model()


class InvitationCreateView(OverheidRoleRequiredMixin, CreateView):
    template_name = "organisaties/overheid_invitation_create.html"
    queryset = LokaleOverheid.objects.all()
    model = User
    required_roles = ["is_beheerder"]
    fields = [
        "email",
        "first_name",
        "last_name",
    ]
    formset_class = RoleInlineFormSet

    def get_lokale_overheid(self):
        self.lokale_overheid = self.get_object()
        return self.lokale_overheid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["lokaleoverheid"] = self.lokale_overheid
        context["formset"] = kwargs.get("formset") or self.formset_class(prefix="form")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = kwargs.get("data")
        if data:
            try:
                user = User.objects.get(email=data["email"])
                kwargs["instance"] = user
            except User.DoesNotExist:
                return kwargs
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = self.formset_class(request.POST, prefix="form")

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset=formset)
        else:
            return self.form_invalid(form, formset=formset)

    def form_valid(self, form, formset=None):
        with transaction.atomic():

            if form.instance.pk:
                self.object = form.instance  # do not update existing user
            else:
                self.object = form.save()
                UserInvitation.objects.create_and_send(self.object, self.request)

            if formset:
                formset.instance = self.object
                self._set_form_lokale_overheid(formset)
                try:
                    formset.save()
                except IntegrityError:
                    messages.add_message(
                        self.request,
                        messages.ERROR,
                        _(
                            "Er bestaat al een gebruiker met dit e-mailadres binnen deze organisatie."
                        ),
                    )

            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset=None):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def get_success_url(self):
        return reverse_lazy(
            "organisaties:overheid_roles", kwargs={"pk": self.lokale_overheid.pk}
        )

    def _set_form_lokale_overheid(self, form):
        for role in form.save(commit=False):
            role.lokale_overheid = self.lokale_overheid


class InvitationAcceptView(SingleObjectMixin, FormView):
    queryset = UserInvitation.objects.filter(accepted=False)
    template_name = "organisaties/overheid_invitation_accept.html"
    form_class = InvitationAcceptForm
    success_url = reverse_lazy("core:home")

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs["key"])
        except UserInvitation.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.object.user
        return context

    def get(self, *args, **kwargs):
        self.object = invitation = self.get_object()
        if not invitation:
            raise Http404()
        return super().get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.accept_invitation(self.request, form.cleaned_data)
        return super().form_valid(form)
