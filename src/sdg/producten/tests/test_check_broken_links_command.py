from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class TestCheckBrokenLinksCommandTestCase(TestCase):
    def call_command(self, command_name, *args, **kwargs):
        out = StringIO()
        call_command(
            command_name,
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_handle_response_code_successful(self):
        out = self.call_command("check_broken_links")
        self.assertIn("Deleted 0 old BrokenLink(s).", out)

    def test_reset_all_broken_links(self):
        out = self.call_command("check_broken_links", "--reset")
        self.assertIn(
            "Successfully cleared the error_count of every BrokenLink.", str(out)
        )
