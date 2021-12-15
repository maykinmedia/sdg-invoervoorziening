from django.contrib import admin

from timeline_logger.models import TimelineLog

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
    list_display = ("event",)
    date_hierarchy = "timestamp"

    def _get_message(self, obj):
        return obj.get_message()

    _get_message.short_description = "Event information"

    def _format_payload(self, payload: dict) -> str:
        if publish := payload.get("publish"):
            publish = publish[0]
            if publish == "date":
                return f" gepubliceerd op datum {payload['date'][0]}"
            else:
                return f" opgeslagen als {publish}"
        return ""

    def event(self, obj):
        title = f"Gebruiker {obj.user} heeft {obj.content_type}"
        result = obj.extra_data["result"]
        payload = obj.extra_data["payload"]

        title += self._format_payload(payload)
        return f"[{obj.timestamp}] {title} ({obj.content_object}) - {result}."

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
