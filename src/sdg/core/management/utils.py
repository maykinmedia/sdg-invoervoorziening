from datetime import datetime
from typing import Any, Dict, List

from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)
from sdg.core.utils import string_to_date


def load_gemeenten(data: List[Dict[str, Any]]) -> int:
    """
    Loads municipalities based on a CSV or XML file.

    :return: The total count of the created objects.
    """
    count = 0

    for obj in data:
        _oo, created = Overheidsorganisatie.objects.update_or_create(
            owms_identifier=obj.get("resourceIdentifier"),
            defaults={
                "owms_pref_label": obj.get("prefLabel"),
                "owms_end_date": string_to_date(obj.get("endDate"), "%Y-%m-%d")
                if obj.get("endDate")
                else None,
            },
        )
        if created:
            count += 1

    return count


def load_informatiegebieden(data: List[Dict[str, Any]]) -> int:
    """
    Loads information areas based on a CSV or XML file.

    :return: The total count of the created objects.
    """

    codes = [obj.pop("SDG_Code") for obj in data]
    grouped_data = dict(zip(codes, data))

    informatiegebied_list = [
        Informatiegebied(
            code=code,
            informatiegebied=obj.get("SDG_Informatiegebied"),
            informatiegebied_uri=obj.get("SDG_IGURI"),
        )
        for code, obj in grouped_data.items()
    ]
    informatiegebieden = Informatiegebied.objects.bulk_create(informatiegebied_list)

    for informatiegebied in informatiegebieden:
        grouped_data.get(informatiegebied.code)["informatiegebied"] = informatiegebied

    thema_list = [
        Thema(
            informatiegebied=obj.get("informatiegebied"),
            thema=obj.get("SDG_Thema"),
            thema_uri=obj.get("SDG_ThemaURI"),
        )
        for obj in grouped_data.values()
    ]

    created_objects = Thema.objects.bulk_create(thema_list)
    return len(created_objects)


def load_upn(data: List[Dict[str, Any]]) -> int:
    """
    Loads UPNs based on a CSV or XML file.

    :return: The total count of the created objects.
    """

    upn_list = [
        UniformeProductnaam(
            upn_uri=obj.get("URI"),
            upn_label=obj.get("UniformeProductnaam"),
            rijk=bool(obj.get("Rijk")),
            provincie=bool(obj.get("Provincie")),
            waterschap=bool(obj.get("Waterschap")),
            gemeente=bool(obj.get("Gemeente")),
            burger=bool(obj.get("Burger")),
            bedrijf=bool(obj.get("Bedrijf")),
            dienstenwet=bool(obj.get("Dienstenwet")),
            sdg=bool(obj.get("SDG")),
            autonomie=bool(obj.get("Autonomie")),
            medebewind=bool(obj.get("Medebewind")),
            aanvraag=bool(obj.get("Aanvraag")),
            subsidie=bool(obj.get("Subsidie")),
            melding=bool(obj.get("Melding")),
            verplichting=bool(obj.get("Verplichting")),
            digi_d_macht=bool(obj.get("DigiDMacht")),
            grondslag=obj.get("Grondslag"),
            grondslaglabel=obj.get("Grondslaglabel"),
            grondslaglink=obj.get("Grondslaglink"),
        )
        for obj in data
    ]
    created_objects = UniformeProductnaam.objects.bulk_create(upn_list)
    return len(created_objects)
