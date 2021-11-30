from typing import Any, Dict, List

from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)
from sdg.core.utils import string_to_date
from sdg.organisaties.models import LokaleOverheid


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
            LokaleOverheid.objects.get_or_create(
                organisatie=organisatie,
                defaults={
                    "bevoegde_organisatie": organisatie,
                    "ondersteunings_organisatie": organisatie,
                    "verantwoordelijke_organisatie": organisatie,
                },
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
        upn, created = UniformeProductnaam.objects.update_or_create(
            upn_uri=obj.get("URI"),
            grondslag=obj.get("Grondslag"),
            defaults={
                "upn_label": obj.get("UniformeProductnaam"),
                "rijk": bool(obj.get("Rijk")),
                "provincie": bool(obj.get("Provincie")),
                "waterschap": bool(obj.get("Waterschap")),
                "gemeente": bool(obj.get("Gemeente")),
                "burger": bool(obj.get("Burger")),
                "bedrijf": bool(obj.get("Bedrijf")),
                "dienstenwet": bool(obj.get("Dienstenwet")),
                "sdg": bool(obj.get("SDG")),
                "autonomie": bool(obj.get("Autonomie")),
                "medebewind": bool(obj.get("Medebewind")),
                "aanvraag": bool(obj.get("Aanvraag")),
                "subsidie": bool(obj.get("Subsidie")),
                "melding": bool(obj.get("Melding")),
                "verplichting": bool(obj.get("Verplichting")),
                "digi_d_macht": bool(obj.get("DigiDMacht")),
                "grondslaglabel": obj.get("Grondslaglabel"),
                "grondslaglink": obj.get("Grondslaglink"),
            },
        )
        if created:
            count += 1

    return count


def load_upn_informatiegebieden(data: List[Dict[str, Any]]) -> int:
    """
    Link existing UPNs and information areas together.

    :return: The total count of updated objects.
    """

    count = 0

    for obj in data:
        try:
            thema = Thema.objects.get(
                thema=obj.get("SDG_Thema"), informatiegebied__code=obj.get("SDG_Code")
            )
        except Thema.DoesNotExist:
            continue

        count += UniformeProductnaam.objects.filter(
            upn_label=obj.get("UniformeProductnaam")
        ).update(thema=thema)

    return count
