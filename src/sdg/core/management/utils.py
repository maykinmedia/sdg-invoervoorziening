import datetime
import logging
import string
from typing import Any

from django.db.models import Q

from sdg.core.constants import DoelgroepChoices, TaalChoices
from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)
from sdg.core.utils import string_to_date
from sdg.organisaties.models import BevoegdeOrganisatie, LokaleOverheid
from sdg.producten.models import (
    GeneriekProduct,
    LocalizedGeneriekProduct,
    ProductVersie,
)

logger = logging.getLogger(__name__)


def load_government_organisations(data: list[dict[str, Any]]) -> int:
    """
    Loads government organisations based on a list of dictionaries.

    :return: The total count of the created objects.
    """
    count = 0
    for obj in data:
        resource_id = obj.get("resourceIdentifier")
        organisatie, created = Overheidsorganisatie.objects.update_or_create(
            owms_identifier=resource_id,
            defaults={
                "owms_pref_label": obj.get("prefLabel"),
                "owms_end_date": (
                    string_to_date(obj.get("endDate"), "%Y-%m-%d")
                    if obj.get("endDate")
                    else None
                ),
            },
        )
        if created:
            count += 1

    return count


def load_organisation_subset(data: list[dict[str, Any]]) -> int:
    """
    Identifies organisations in the list of all government organisations. It
    specifically does not add any organiation if it's not in the list of
    government organisations.

    WARNING: Depends on `load_government_organisations`.

    :return: The total count of the created objects.
    """
    gov_orgs = {obj.owms_identifier: obj for obj in Overheidsorganisatie.objects.all()}

    count = 0
    for obj in data:
        gov_org = gov_orgs.get(obj.get("resourceIdentifier"), None)
        if gov_org is not None:
            municipality, created = LokaleOverheid.objects.get_or_create(
                organisatie=gov_org,
            )
            if created:
                BevoegdeOrganisatie.objects.create(
                    lokale_overheid=municipality, organisatie=gov_org
                )
            if created:
                count += 1

    return count


def load_informatiegebieden(data: list[dict[str, Any]]) -> int:
    """
    Loads information areas based on a list of dictionaries.

    :return: The total count of the created objects.
    """
    igs = {obj.get("SDG_IGURI"): obj.get("SDG_Informatiegebied") for obj in data}

    for ig_uri, ig_name in igs.items():
        informatiegebied, created = Informatiegebied.objects.update_or_create(
            informatiegebied_uri=ig_uri,
            defaults={
                "informatiegebied": ig_name,
            },
        )

    count_themas = 0

    for obj in data:
        thema, created = Thema.objects.update_or_create(
            thema_uri=obj.get("SDG_ThemaURI"),
            defaults={
                "code": obj.get("SDG_Code"),
                "thema": obj.get("SDG_Thema"),
                "informatiegebied": Informatiegebied.objects.filter(
                    informatiegebied_uri=obj.get("SDG_IGURI")
                ).first(),
            },
        )
        if created:
            count_themas += 1

    return count_themas


def load_upn(data: list[dict[str, Any]]) -> int:
    """
    Loads UPNs based on a list of dictionaries.

    :return: The total count of the created objects.
    """
    count = 0
    upn_updated_list = []

    for obj in data:
        sdg_list = sdg.split(";") if (sdg := obj.get("SDG")) else []

        # TODO: This is a bit of a hack. We should probably use a
        #       ManyToManyField.
        theme = Thema.objects.filter(code__in=sdg_list).first()

        upn, created = UniformeProductnaam.objects.update_or_create(
            upn_uri=obj.get("URI"),
            defaults={
                "upn_label": obj.get("UniformeProductnaam"),
                "rijk": bool(obj.get("Rijk")),
                "provincie": bool(obj.get("Provincie")),
                "waterschap": bool(obj.get("Waterschap")),
                "gemeente": bool(obj.get("Gemeente")),
                "burger": bool(obj.get("Burger")),
                "bedrijf": bool(obj.get("Bedrijf")),
                "dienstenwet": bool(obj.get("Dienstenwet")),
                # The "sdg"-column got changed (without any notice or sense of
                # versioning) from boolean to the relevant SDG code(s). For us,
                # it's just important we know that this UPN concerns the SDG
                # and we will obtain the SDG codes via another way.
                "sdg": sdg_list,
                "autonomie": bool(obj.get("Autonomie")),
                "medebewind": bool(obj.get("Medebewind")),
                "aanvraag": bool(obj.get("Aanvraag")),
                "subsidie": bool(obj.get("Subsidie")),
                "melding": bool(obj.get("Melding")),
                "verplichting": bool(obj.get("Verplichting")),
                "digi_d_macht": bool(obj.get("DigiDMacht")),
                # We leave out the "grondslagen" (legal basis) data because
                # there can be more than 1 for a UPN. We don't use them at the
                # moment so they are ignored.
                "thema": theme,
                "is_verwijderd": False,
            },
        )
        upn_updated_list.append(upn.pk)

        if created:
            count += 1

    UniformeProductnaam.objects.filter(~Q(pk__in=upn_updated_list)).update(
        is_verwijderd=True
    )

    # Update generic products.
    for upn in UniformeProductnaam.objects.all():
        update_generic_products(upn)

    return count


def update_generic_products(upn):
    """
    Update all generic products that belong to this UPN. At the moment this can
    be 0, 1 or 2. If a UPN is not meant for the SDG, the result will be 0. If
    the UPN contains 2 SDG codes that belong to different target groups
    (eu-burger or eu-bedrijf), the result will be 2 generic products.

    Missing generic products will be created.

    Obsolete generic products will be deleted or, if this is not possible, it
    will be marked as end of life.
    """

    def _get_group(sdg_code: str) -> str:
        """Get the target group from a given SDG code.
        - The range A-I equals "burger".
        - The range J+ equals "bedrijf".
        """
        letter = sdg_code[0]
        if letter in string.ascii_uppercase[:9]:
            return DoelgroepChoices.burger
        elif letter in string.ascii_uppercase[9:]:
            return DoelgroepChoices.bedrijf

    def _clean_other_generic_products(upn, valid_generic_products):
        """
        Set an end date on generic products (attached to given UPN) that are
        not in the list of `valid_generic_products`

        It's possible existing generic products were created when the UPN had
        different properties (like an SDG code that was later removed). These
        generic products need to be cleaned up. We cannot just delete them,
        since they have relations and we should not delete anything that could
        have user data.
        """
        correct_gp_pks = [gp_i.pk for gp_i in valid_generic_products]
        for existing_gp in list(upn.generieke_producten.exclude(pk__in=correct_gp_pks)):
            if existing_gp.eind_datum is not None:
                # This generic product is marked as end of life. Leave it
                # alone.
                continue

            # Attempt to delete the generic product...
            if not _try_delete_generic_product(existing_gp):
                # If that fails, mark it as end of life.
                logger.info(
                    f'Marking generic product "{upn} ({existing_gp.pk}) as end of life".'
                )
                existing_gp.eind_datum = datetime.date.today()
                existing_gp.save()

    def _try_delete_generic_product(generic_product):
        active_versions = ProductVersie.objects.filter(
            product__generiek_product=generic_product, publicatie_datum__isnull=False
        ).count()

        if active_versions == 0:
            logger.info(
                f"Deleting generic product {generic_product.upn} ({generic_product.pk}) since there are no active specific products."
            )
            generic_product.producten.exclude(referentie_product=None).delete()
            generic_product.producten.filter(referentie_product=None).delete()
            generic_product.delete()
            return True

        logger.warning(
            f"Cannot delete generic product {generic_product.upn} ({generic_product.pk}) since there are active specific products."
        )
        return False

    # Create generic product (and localize) for each target group
    groups = [doelgroep for i in upn.sdg if (doelgroep := _get_group(i))]

    generic_products = []
    for group in groups:
        (
            generic_product,
            g_created,
        ) = GeneriekProduct.objects.get_or_create(
            upn=upn,
            doelgroep=group,
        )
        generic_products.append(generic_product)

        if g_created:
            logger.info(f'Created new generic product for "{upn} ({group})".')
            LocalizedGeneriekProduct.objects.localize(
                instance=generic_product,
                languages=TaalChoices.get_available_languages(),
            )
    # Now that we have the proper generic products, we can clean any others.
    _clean_other_generic_products(upn, generic_products)
