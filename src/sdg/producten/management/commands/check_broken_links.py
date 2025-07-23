from django.core.management import BaseCommand

from ...broken_links import check_broken_link, reset_broken_links


class Command(BaseCommand):
    help = "Check for broken links in product fields and update the BrokenLink model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            "-R",
            action="store_true",
            help="Reset all the broken links.",
        )

    def handle(self, **options):
        # Handle Reset
        if options.get("reset"):
            reset_broken_links(reset_all=True)
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully cleared the error_count of every BrokenLink."
                )
            )
            return

        total = check_broken_link()
        self.stdout.write(self.style.SUCCESS(f"Deleted {total} old BrokenLink(s)."))
