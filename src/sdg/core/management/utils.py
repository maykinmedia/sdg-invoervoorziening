import string
from typing import Any, Dict, List

from sdg.core.constants import TaalChoices
from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)
from sdg.core.utils import string_to_date
from sdg.organisaties.models import BevoegdeOrganisatie, LokaleOverheid
from sdg.producten.models import GeneriekProduct, LocalizedGeneriekProduct


def load_gemeenten(data: List[Dict[str, Any]]) -> int:
    """
    Loads municipalities based on a list of dictionaries.

    :return: The total count of the created objects.
    """

    def _is_municipality(resource_identifier: str) -> bool:
        return resource_identifier.endswith("(gemeente)")

    count = 0
    for obj in data:
        resource_id = obj.get("resourceIdentifier")
        organisatie, created = Overheidsorganisatie.objects.update_or_create(
            owms_identifier=resource_id,
            defaults={
                "owms_pref_label": obj.get("prefLabel"),
                "owms_end_date": string_to_date(obj.get("endDate"), "%Y-%m-%d")
                if obj.get("endDate")
                else None,
            },
        )
        if _is_municipality(resource_id):
            municipality, created = LokaleOverheid.objects.get_or_create(
                organisatie=organisatie,
                defaults={
                    "ondersteunings_organisatie": organisatie,
                },
            )
            if created:
                BevoegdeOrganisatie.objects.create(
                    organisatie=organisatie,
                    lokale_overheid=municipality,
                    naam=organisatie.owms_pref_label,
                )
        if created:
            count += 1

    return count


def load_informatiegebieden(data: List[Dict[str, Any]]) -> int:
    """
    Loads information areas based on a list of dictionaries.

    :return: The total count of the created objects.
    """

    codes = [obj.pop("SDG_Code") for obj in data]
    grouped_data = dict(zip(codes, data))

    for code, obj in grouped_data.items():
        informatiegebied, created = Informatiegebied.objects.update_or_create(
            code=code,
            defaults={
                "informatiegebied": obj.get("SDG_Informatiegebied"),
                "informatiegebied_uri": obj.get("SDG_IGURI"),
            },
        )

        obj["informatiegebied"] = informatiegebied

    count_themas = 0

    for obj in grouped_data.values():
        thema, created = Thema.objects.update_or_create(
            thema_uri=obj.get("SDG_ThemaURI"),
            defaults={
                "thema": obj.get("SDG_Thema"),
                "informatiegebied": obj.get("informatiegebied"),
            },
        )
        if created:
            count_themas += 1

    return count_themas


def load_upn(data: List[Dict[str, Any]]) -> int:
    """
    Loads UPNs based on a list of dictionaries.

    :return: The total count of the created objects.
    """
    count = 0

    for obj in data:
        sdg_list = sdg.split(";") if (sdg := obj.get("SDG")) else []

        # TODO: This is a bit of a hack. We should probably use a
        #       ManyToManyField.
        theme = Thema.objects.filter(informatiegebied__code__in=sdg_list).first()

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
            },
        )

        groups = [doelgroep for i in sdg_list if (doelgroep := _get_group(i))]
        # Create generic product (and localize) for each target group
        for group in groups:
            generic, g_created = GeneriekProduct.objects.get_or_create(
                upn=upn,
                doelgroep=group,
            )
            if g_created:
                LocalizedGeneriekProduct.objects.localize(
                    instance=generic,
                    languages=TaalChoices.get_available_languages(),
                )

        if created:
            count += 1

    return count


def _get_group(sdg_code: str) -> str:
    """Get the target group from a given SDG code.
    - The range A-I equals "burger".
    - The range J+ equals "bedrijf".
    """
    letter = sdg_code[0]
    if letter in string.ascii_uppercase[:9]:
        return "eu-burger"
    elif letter in string.ascii_uppercase[9:]:
        return "eu-bedrijf"
