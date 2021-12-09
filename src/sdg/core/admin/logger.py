from django.contrib import admin
from django.urls import path

from timeline_logger.models import TimelineLog
from timeline_logger.views import TimelineLogListView

admin.site.unregister(TimelineLog)


@admin.register(TimelineLog)
class TimelineLogAdmin(admin.ModelAdmin):
    fields = (
        "timestamp",
        "user",
        "_get_message",
    )
    search_fields = (
        "extra_data",
        "object_id",
    )
    date_hierarchy = "timestamp"

    def _get_message(self, obj):
        return obj.get_message()

    _get_message.short_description = "Event information"

    def get_urls(self):
        return [
            path(
                "auditlog/",
                self.admin_site.admin_view(TimelineLogListView.as_view()),
                name="audit-log",
            ),
        ] + super().get_urls()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
