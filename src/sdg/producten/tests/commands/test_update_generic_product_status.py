from datetime import datetime, timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import now

from sdg.core.constants import GenericProductStatus
from sdg.producten.tests.factories.product import GeneriekProductFactory


class UpdateGenericProductStatusTests(TestCase):
    def test_update_generic_product_status_expired(self):
        generic = GeneriekProductFactory.create(
            upn__is_verwijderd=True,
            eind_datum=None,
            product_status=GenericProductStatus.NEW,
        )
        self.assertEqual(generic.product_status, GenericProductStatus.NEW)

        call_command("update_generic_product_status")

        generic.refresh_from_db()
        self.assertEqual(generic.product_status, GenericProductStatus.EXPIRED)

    def test_update_generic_product_status_eol_deleted(self):
        generic_1 = GeneriekProductFactory.create(
            eind_datum=now() - timedelta(days=1),
            product_status=GenericProductStatus.NEW,
        )

        generic_2 = GeneriekProductFactory.create(
            eind_datum=now() + timedelta(days=1),
            product_status=GenericProductStatus.NEW,
        )

        self.assertEqual(generic_1.product_status, GenericProductStatus.NEW)
        self.assertEqual(generic_2.product_status, GenericProductStatus.NEW)

        call_command("update_generic_product_status")

        generic_1.refresh_from_db()
        generic_2.refresh_from_db()
        self.assertEqual(generic_1.product_status, GenericProductStatus.DELETED)
        self.assertEqual(generic_2.product_status, GenericProductStatus.EOL)

    def test_update_generic_product_status_missing(self):
        generic = GeneriekProductFactory.create(
            localized=True, product_status=GenericProductStatus.NEW
        )
        self.assertEqual(generic.product_status, GenericProductStatus.NEW)

        call_command("update_generic_product_status")

        generic.refresh_from_db()
        self.assertEqual(generic.product_status, GenericProductStatus.MISSING)
