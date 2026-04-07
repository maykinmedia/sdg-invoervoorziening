from functools import partial

from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from privates.admin import PrivateMediaMixin
from privates.views import PrivateMediaView

from ..models import ApplicationRapport
from ..tasks import create_application_export


@staff_member_required
@transaction.atomic()
def application_export(requests):
    rapport_export = ApplicationRapport.objects.create(
        gemaakt_op=timezone.now(),
    )
    transaction.on_commit(
        partial(
            create_application_export.delay,
            application_export_pk=rapport_export.pk,
        )
    )

    messages.add_message(
        requests,
        messages.SUCCESS,
        _(
            "Het rapport wordt ge-exporteert, u kunt hem binnen "
            "enkele minuten hier vinden/downloaden."
        ),
    )

    return redirect(reverse("admin:core_applicationrapport_changelist"))


class ReportMediaView(PrivateMediaView):
    def get_sendfile_opts(self):
        object = self.get_object()
        return {
            "attachment": True,
            "attachment_filename": object.file.name,
            "mimetype": "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet",
        }


@admin.register(ApplicationRapport)
class ApplicationExportsAdmin(PrivateMediaMixin, admin.ModelAdmin):
    date_hierarchy = "gemaakt_op"
    list_display = (
        "gemaakt_op",
        "status",
        "download",
    )
    list_display_links = None

    private_media_fields = ("file",)
    private_media_view_class = ReportMediaView

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description=_("Export status"))
    def status(self, obj: ApplicationRapport) -> str:
        if obj.file:
            return _("compleet")

        return _("bezig...")

    @admin.display(description=_("Application rapports"), empty_value="")
    def download(self, obj: ApplicationRapport) -> str:

        if obj.file:
            return format_html(
                '<a href="{url}" download>{text}</a>',
                url=reverse(
                    "admin:core_applicationrapport_file",
                    kwargs={"pk": obj.pk},
                ),
                text=_("Download rapport"),
            )
