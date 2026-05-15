import datetime
import json
from dataclasses import dataclass, field
from typing import assert_never

from django.conf import settings
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import (
    CharField,
    Count,
    F,
    JSONField,
    OuterRef,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce, Concat, JSONObject
from django.db.models.query import QuerySet
from django.utils import timezone

import pandas as pd

from sdg.accounts.models import Role, UserInvitation
from sdg.core.constants import (
    AccountStatus,
    DoelgroepChoices,
    GenericProductStatus,
    Rol,
    Systeemrechten,
    TaalChoices,
)
from sdg.core.models import Overheidsorganisatie, ProductenCatalogus
from sdg.producten.models import (
    LocalizedGeneriekProduct,
    LocalizedProduct,
    ProductVersie,
)


@dataclass
class SpecifiekProduct:
    product_titel_decentraal: str = ""
    specifieke_tekst: str = ""
    verwijzing_links: list | list[list[str]] = field(default_factory=list)
    datum_wijziging: datetime.datetime = None
    procedure_beschrijving: str = ""
    vereisten: str = ""
    bewijs: str = ""
    bezwaar_en_beroep: str = ""
    kosten_en_betaalmethoden: str = ""
    uiterste_termijn: str = ""
    wtd_bij_geen_reactie: str = ""
    decentrale_procedure_label: str = ""
    decentrale_procedure_link: str = ""
    product_valt_onder_toelichting: str = ""
    product_aanwezig_toelichting: str = ""


class ApplicationExporter:
    def __init__(self, file):
        with pd.ExcelWriter(file, engine="xlsxwriter") as writer:
            self.account_data().to_excel(writer, sheet_name="Accounts info")
            self.municipality_data().to_excel(writer, sheet_name="Document info")
            self.product_data().to_excel(writer, sheet_name="Product info")

            for sheet in writer.sheets.values():
                sheet.autofit()

    def _datetime_formater(self, value: datetime.datetime | None | str) -> str:
        if not value:
            return ""

        if isinstance(value, str):
            value = timezone.datetime.fromisoformat(value)

        return value.strftime("%-d %B, %Y, %H:%M")

    def _date_formater(self, value: datetime.date | None | str) -> str:
        if not value:
            return ""

        if isinstance(value, str):
            value = timezone.datetime.fromisoformat(value)

        return value.strftime("%-d %B, %Y")

    def product_data(self) -> pd.DataFrame:
        product_data = []

        def specifiek_product_subquery(langauge: str) -> QuerySet[LocalizedProduct]:
            return (
                LocalizedProduct.objects.filter(
                    product_versie__pk=OuterRef("pk"), taal=langauge
                )
                .order_by("-taal")
                .values(
                    json=JSONObject(
                        product_titel_decentraal="product_titel_decentraal",
                        specifieke_tekst="specifieke_tekst",
                        verwijzing_links="verwijzing_links",
                        datum_wijziging="datum_wijziging",
                        procedure_beschrijving="procedure_beschrijving",
                        vereisten="vereisten",
                        bewijs="bewijs",
                        bezwaar_en_beroep="bezwaar_en_beroep",
                        kosten_en_betaalmethoden="kosten_en_betaalmethoden",
                        uiterste_termijn="uiterste_termijn",
                        wtd_bij_geen_reactie="wtd_bij_geen_reactie",
                        decentrale_procedure_label="decentrale_procedure_label",
                        decentrale_procedure_link="decentrale_procedure_link",
                        product_valt_onder_toelichting="product_valt_onder_toelichting",
                        product_aanwezig_toelichting="product_aanwezig_toelichting",
                    )
                )
            )

        def landelijke_link_subquery(
            langauge: str,
        ) -> QuerySet[LocalizedGeneriekProduct]:
            return LocalizedGeneriekProduct.objects.filter(
                generiek_product__producten__pk=OuterRef("product__pk"),
                taal=langauge,
            ).values("landelijke_link")

        def url_portaal_bedrijf(
            landelijke_link: str, dop: str, language: TaalChoices
        ) -> str:
            if not landelijke_link or not dop:
                return ""

            match language:
                case TaalChoices.nl:
                    return settings.SDG_DOP_URL_TEMPLATE_NL.format(
                        product_url=landelijke_link, organisation=dop
                    )
                case TaalChoices.en:
                    return settings.SDG_DOP_URL_TEMPLATE_EN.format(
                        product_url=landelijke_link, organisation=dop
                    )
                case _:  # pragma: no cover
                    assert_never(language)

        def url_portaal_burger(
            landelijke_link: str, dpc: str, language: TaalChoices
        ) -> str:
            if not landelijke_link or not dpc:
                return ""

            match language:
                case TaalChoices.nl:
                    return settings.SDG_DPC_URL_TEMPLATE_NL.format(
                        product_url=landelijke_link, organisation=dpc
                    )
                case TaalChoices.en:
                    return settings.SDG_DPC_URL_TEMPLATE_EN.format(
                        product_url=landelijke_link, organisation=dpc
                    )
                case _:  # pragma: no cover
                    assert_never(language)

        verantwoordelijke_organisaties_subquery = Overheidsorganisatie.objects.filter(
            generiekproduct__pk=OuterRef("product__generiek_product__pk")
        ).values_list("owms_pref_label", flat=True)

        organisatie_subquery = Overheidsorganisatie.objects.filter(
            pk=OuterRef("product__catalogus__lokale_overheid__organisatie__pk")
        ).values(
            json=JSONObject(
                gemeente="owms_pref_label",
                dop="dop_slug",
                dpc="dpc_slug",
            )
        )

        for version in (
            ProductVersie.objects.select_related(
                "product", "product__generiek_product", "product__bevoegde_organisatie"
            )
            .exclude(
                product__catalogus__lokale_overheid__organisatie__owms_end_date__lte=timezone.now(),
            )
            .filter(
                (
                    (
                        Q(publicatie_datum__isnull=False)
                        & Q(publicatie_datum__lte=timezone.now())
                    )
                    | (
                        Q(versie=1)
                        & (
                            Q(publicatie_datum__isnull=True)
                            | Q(publicatie_datum__gt=timezone.now())
                        )
                    )
                ),
                product__generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION,
            )
            .order_by("product__catalogus__pk", "product__pk", "-versie")
            .distinct("product__catalogus__pk", "product__pk")
            .annotate(
                specifiek_nl=Coalesce(
                    Subquery(
                        specifiek_product_subquery(langauge="nl")[:1],
                        output_field=JSONField(),
                    ),
                    Value("{}"),
                    output_field=JSONField(),
                )
            )
            .annotate(
                specifiek_en=Coalesce(
                    Subquery(
                        specifiek_product_subquery(langauge="en")[:1],
                        output_field=JSONField(),
                    ),
                    Value("{}"),
                    output_field=JSONField(),
                )
            )
            .annotate(
                landelijke_link_nl=Subquery(landelijke_link_subquery(langauge="nl")[:1])
            )
            .annotate(
                landelijke_link_en=Subquery(landelijke_link_subquery(langauge="en")[:1])
            )
            .annotate(
                landelijke_verantwoordelijke_organisaties=ArraySubquery(
                    verantwoordelijke_organisaties_subquery
                )
            )
            .annotate(
                informatiegebied=F(
                    "product__generiek_product__upn__thema__informatiegebied__informatiegebied"
                )
            )
            .annotate(product_name=F("product__generiek_product__upn__upn_label"))
            .annotate(
                organisatie=Subquery(organisatie_subquery[:1], output_field=JSONField())
            )
            .annotate(
                valt_onder=F(
                    "product__product_valt_onder__generiek_product__upn__upn_label"
                )
            )
            .annotate(
                valt_onder_doelgroep=F(
                    "product__product_valt_onder__generiek_product__doelgroep"
                )
            )
        ):
            doelgroep = version.product.generiek_product.doelgroep
            specifiek_nl = SpecifiekProduct(**version.specifiek_nl)
            specifiek_en = SpecifiekProduct(**version.specifiek_en)

            match doelgroep:
                case DoelgroepChoices.bedrijf:
                    url_portaal = url_portaal_bedrijf(
                        version.landelijke_link_nl,
                        version.organisatie.get("dop", ""),
                        TaalChoices.nl,
                    )
                    url_portaal_en = url_portaal_bedrijf(
                        version.landelijke_link_en,
                        version.organisatie.get("dop", ""),
                        TaalChoices.en,
                    )
                case DoelgroepChoices.burger:
                    url_portaal = url_portaal_burger(
                        version.landelijke_link_nl,
                        version.organisatie.get("dpc", ""),
                        TaalChoices.nl,
                    )
                    url_portaal_en = url_portaal_burger(
                        version.landelijke_link_en,
                        version.organisatie.get("dpc", ""),
                        TaalChoices.en,
                    )
                case _:
                    url_portaal = ""
                    url_portaal_en = ""

            product_data.append(
                {
                    "id": version.product.pk,
                    "gemeente": version.organisatie["gemeente"],
                    "doelgroep": doelgroep,
                    "UPN label": version.product_name,
                    "status": version.current_status,
                    "aanwezig": version.product.product_aanwezig,
                    "heeft kosten": version.product.heeft_kosten,
                    "aanwezig toelichting": specifiek_nl.product_aanwezig_toelichting,
                    "aanwezig toelichting (en)": specifiek_en.product_aanwezig_toelichting,
                    "valt onder doelgroep": version.valt_onder_doelgroep,
                    "valt onder": version.valt_onder,
                    "valt onder toelichting": specifiek_nl.product_valt_onder_toelichting,
                    "valt onder toelichting (en)": specifiek_en.product_valt_onder_toelichting,
                    "valt onder(ja / nee)": "Ja" if version.valt_onder else "Nee",
                    "informatiegebied": version.informatiegebied,
                    "SDG product": version.product_name,
                    "specifieke titel": specifiek_nl.product_titel_decentraal,
                    "specifieke titel (en)": specifiek_en.product_titel_decentraal,
                    "specifieke tekst": specifiek_nl.specifieke_tekst,
                    "specifieke tekst (en)": specifiek_en.specifieke_tekst,
                    "procedure beschrijving": specifiek_nl.procedure_beschrijving,
                    "procedure beschrijving (en)": specifiek_en.procedure_beschrijving,
                    "vereisten": specifiek_nl.vereisten,
                    "vereisten (en)": specifiek_en.vereisten,
                    "bewijs": specifiek_nl.bewijs,
                    "bewijs (en)": specifiek_en.bewijs,
                    "bezwaar en beroep": specifiek_nl.bezwaar_en_beroep,
                    "bezwaar en beroep (en)": specifiek_en.bezwaar_en_beroep,
                    "kosten en betaalmethoden": specifiek_nl.kosten_en_betaalmethoden,
                    "kosten en betaalmethoden (en)": specifiek_en.kosten_en_betaalmethoden,
                    "uiterste termijn": specifiek_nl.uiterste_termijn,
                    "uiterste termijn (en)": specifiek_en.uiterste_termijn,
                    "wat te doen bij geen reactie": specifiek_nl.wtd_bij_geen_reactie,
                    "wat te doen bij geen reactie (en)": specifiek_en.wtd_bij_geen_reactie,
                    "specifieke verwijzing links": specifiek_nl.verwijzing_links,
                    "specifieke verwijzing links (en)": specifiek_en.verwijzing_links,
                    "URL portaal": url_portaal,
                    "URL portaal (en)": url_portaal_en,
                    "decentrale procedure label": specifiek_nl.decentrale_procedure_label,
                    "decentrale procedure label (en)": specifiek_en.decentrale_procedure_label,
                    "decentrale procedure link": specifiek_nl.decentrale_procedure_link,
                    "decentrale procedure link (en)": specifiek_en.decentrale_procedure_link,
                    "landelijk verantwoordelijke organisatie": ", ".join(
                        version.landelijke_verantwoordelijke_organisaties
                    ),
                    "gemaakt op": self._datetime_formater(version.gemaakt_op),
                    "publicatiedatum": self._date_formater(version.publicatie_datum),
                    "laatste wijziging": self._datetime_formater(version.gewijzigd_op),
                    "versie": version.versie,
                    "bevoegde organisatie": version.product.bevoegde_organisatie.naam,
                }
            )

        return pd.DataFrame(product_data)

    def account_data(self) -> pd.DataFrame:
        account_data = []

        user_invitation_subquery: QuerySet[UserInvitation] = (
            UserInvitation.objects.select_related("inviter")
            .filter(user__pk=OuterRef("user__pk"))
            .values(
                json=JSONObject(
                    accepted="accepted",
                    created="created",
                    name=Concat(
                        F("inviter__first_name"),
                        Value(" "),
                        F("inviter__last_name"),
                        output_field=CharField(),
                    ),
                )
            )
        )

        for role in (
            Role.objects.select_related("user", "lokale_overheid")
            .annotate(
                organisation_name=F("lokale_overheid__organisatie__owms_pref_label")
            )
            .annotate(
                inviter=Coalesce(
                    Subquery(user_invitation_subquery[:1], output_field=JSONField()),
                    Value(json.dumps({"accepted": "", "created": "", "name": ""})),
                    output_field=JSONField(),
                )
            )
            .order_by("user__pk", "-user__date_joined")
            .values(
                "user__pk",
                "lokale_overheid__pk",
                "organisation_name",
                "organisation_name",
                "user__first_name",
                "user__last_name",
                "user__email",
                "user__date_joined",
                "user__last_login",
                "user__is_active",
                "is_beheerder",
                "is_redacteur",
                "is_raadpleger",
                "user__is_superuser",
                "user__is_staff",
                "user__is_superuser",
                "user__is_staff",
                "inviter",
            )
        ):
            account_status = AccountStatus.empty.label
            if role["user__last_login"]:
                account_status = AccountStatus.logged_in.label
            elif role["inviter"]["created"]:
                account_status = AccountStatus.created.label

            rol = Rol.empty.label
            if role["is_beheerder"]:
                rol = Rol.is_beheerder.label
            elif role["is_redacteur"]:
                rol = Rol.is_redacteur.label
            elif role["is_raadpleger"]:
                rol = Rol.is_raadpleger.label

            systeemrechten = Systeemrechten.empty.label
            if role["user__is_superuser"]:
                systeemrechten = Systeemrechten.is_superuser.label
            elif role["user__is_staff"]:
                systeemrechten = Systeemrechten.is_staff.label

            account_data.append(
                {
                    "id": role["user__pk"],
                    "gemeente_id": role["lokale_overheid__pk"],
                    "organisatie": role["organisation_name"],
                    "gemeente": role["organisation_name"],
                    "voornaam": role["user__first_name"],
                    "achternaam": role["user__last_name"],
                    "naam": f"{role['user__first_name']} {role['user__last_name']}",
                    "email": role["user__email"],
                    "uitgenodigd door": role["inviter"]["name"],
                    "date_joined": self._datetime_formater(role["user__date_joined"]),
                    "last_login": self._datetime_formater(role["user__last_login"]),
                    "account status": account_status,
                    "accepted": role["inviter"]["accepted"],
                    "created": self._datetime_formater(role["inviter"]["created"]),
                    "is_active": role["user__is_active"],
                    "rol": rol,
                    "is_beheerder": role["is_beheerder"],
                    "is_redacteur": role["is_redacteur"],
                    "is_raadpleger": role["is_raadpleger"],
                    "systeemrechten": systeemrechten,
                    "is_superuser": role["user__is_superuser"],
                    "is_staff": role["user__is_staff"],
                }
            )

        return pd.DataFrame(account_data)

    def municipality_data(self) -> pd.DataFrame:
        municipality_data = []

        published_product_count_subquery: QuerySet[ProductVersie] = (
            ProductVersie.objects.select_related("product", "product__catalogus")
            .filter(
                product__catalogus__pk=OuterRef("pk"),
                product__generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION,
                publicatie_datum__lte=timezone.now(),
            )
            .order_by("product__pk", "pk", "-versie")
            .distinct("product__pk")
            .values("product__pk")
        )

        concept_product_count_subquery: QuerySet[ProductVersie] = (
            ProductVersie.objects.select_related("product")
            .filter(
                product__catalogus__pk=OuterRef("pk"),
                product__generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION,
                publicatie_datum=None,
                versie=1,
            )
            .values("product__pk")
        )

        for catalog in (
            ProductenCatalogus.objects.exclude(
                lokale_overheid__organisatie__owms_end_date__lte=timezone.now()
            )
            .annotate(gemeente=F("lokale_overheid__organisatie__owms_pref_label"))
            .annotate(
                total=Count(
                    "producten",
                    filter=Q(
                        producten__generiek_product__product_status=GenericProductStatus.READY_FOR_PUBLICATION
                    ),
                )
            )
            .annotate(
                published_products=ArraySubquery(published_product_count_subquery)
            )
            .annotate(concept_products=ArraySubquery(concept_product_count_subquery))
            .iterator()
        ):
            municipality_data.append(
                {
                    "gemeente": catalog.gemeente,
                    "aantal gepubliceerde teksten": len(
                        catalog.published_products
                    ).__str__(),
                    "aantal conceptteksten": len(catalog.concept_products).__str__(),
                    "aantal teksten": catalog.total.__str__(),
                }
            )

        return pd.DataFrame(municipality_data)
