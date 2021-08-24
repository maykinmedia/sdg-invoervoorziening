from datetime import datetime
from typing import Dict, Any, List

from sdg.core.models import (
    Overheidsorganisatie,
    UniformeProductnaam,
    Informatiegebied,
    Thema,
)
from sdg.core.utils import string_to_date


def load_gemeenten(data: List[Dict[str, Any]]) -> int:
    """
    Laadt gemeenten op basis van een CSV/XML-bestand.

    :return: De totale telling van de gecreëerde objecten.
    """

    gemeente_list = [
        Overheidsorganisatie(
            owms_identifier=obj.get("prefLabel"),
            owms_pref_label=obj.get("resourceIdentifier"),
            owms_end_date=string_to_date(obj.get("endDate"), "%Y-%m-%d")
            if obj.get("endDate")
            else None,
        )
        for obj in data
    ]
    created_objects = Overheidsorganisatie.objects.bulk_create(gemeente_list)
    return len(created_objects)


def load_informatiegebieden(data: List[Dict[str, Any]]) -> int:
    """
    Laadt informatiegebieden op basis van een CSV/XML-bestand.

    :return: De totale telling van de gecreëerde objecten.
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
    Laadt uniformeproductnamen op basis van een CSV/XML-bestand.

    :return: De totale telling van de gecreëerde objecten.
    """

    upn_list = [
        UniformeProductnaam(
            upn_uri=obj.get("URI"),
            upn_label=obj.get("UniformeProductnaam"),
            rijk=bool(obj.get("Rijk")),
            provincie=bool(obj.get("Provincie")),
            waterschap=bool(obj.get("Waterschap")),
            gemeente= bool(obj.get("Gemeente")),
            burger=bool(obj.get("Burger")),
            bedrijf=bool(obj.get("Bedrijf")),
            dienstenwet= bool(obj.get("Dienstenwet")),
            sdg= bool(obj.get("SDG")),
            autonomie= bool(obj.get("Autonomie")),
            medebewind= bool(obj.get("Medebewind")),
            aanvraag= bool(obj.get("Aanvraag")),
            subsidie= bool(obj.get("Subsidie")),
            melding= bool(obj.get("Melding")),
            verplichting= bool(obj.get("Verplichting")),
            digi_d_macht=bool(obj.get("DigiDMacht")),
            grondslag=obj.get("Grondslag"),
            grondslaglabel=obj.get("Grondslaglabel"),
            grondslaglink=obj.get("Grondslaglink"),
        ) for obj in data
    ]
    created_objects = UniformeProductnaam.objects.bulk_create(upn_list)
    return len(created_objects)
