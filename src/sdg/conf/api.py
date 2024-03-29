from vng_api_common.conf.api import *  # noqa

# DRF
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": ["sdg.api.authentication.TokenAuthentication"],
    "DEFAULT_THROTTLE_CLASSES": [
        "sdg.api.throttling.CustomRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"user": "100/min"},
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "EXCEPTION_HANDLER": "vng_api_common.views.exception_handler",
    "PAGE_SIZE": 25,
}

description = f"""
## Introductie
Deze API stelt u in staat om productbeschrijvingen te beheren voor producten
die relevant zijn voor de SDG-verordening. De API is gebaseerd op het SDG
informatiemodel versie 1.6.

## Authenticatie en autorisatie
De API is zonder authenticatie toegankelijk voor lees-toegang.

Wilt u zeer veel verzoeken maken naar deze API, dan dient u een API-token te
gebruiken (zie: Throttling). Ook voor schrijf-toegang heeft u een API-token
nodig. Het API-token dient u mee te geven bij ieder verzoek in de header, als
volgt: `Authorization: Token <token>` waar `<token>` vervangen dient te worden
met de waarde van het token.

Het aanvragen van een API-token is op dit moment niet mogelijk.

## Throttling
Zonder API-token bent u gelimiteerd in het aantal verzoeken dat u kunt doen,
namelijk: {REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"]}. Als u wel in het
bezit bent van een API-token is er geen limiet.

## Identificerende sleutels
In de API wordt gebruik gemaakt van een identificerende sleutels voor producten
en organisaties zoals die bekend zijn bij de
[Rijksoverheid](https://standaarden.overheid.nl/).

Voor producten wordt gebruik gemaakt van de
[Uniforme Productnamenlijst (UPL)](https://standaarden.overheid.nl/upl). De
relevante velden in deze API worden aangeduid met de
`upnIdentificatie`.

Voor organisaties wordt gebruik gemaakt van
[OWMS waardenlijsten](https://standaarden.overheid.nl/owms/4.0/doc/waardelijsten).
De velden in deze API worden aangeduid met de
`(organisatie)OwmsIdentifier`. Afhankelijk van de resource staat het woord
"organisatie" (of iets anders) er wel of niet voor.

Alle objecten worden tevens geïdentificeerd met een
[UUID](https://nl.wikipedia.org/wiki/Universally_unique_identifier). Objecten
die geen Rijksbrede identificatie kennen, hebben enkel een UUID. UUIDs zijn
daarom alleen relevant in gebruik met deze API.

## Ondersteuning voor Markdown
Sommige velden in de API ondersteunen
de basisset van het
[Markdown formaat](https://www.markdownguide.org/basic-syntax/). Op deze
basisset gelden ook nog een aantal uitzonderingen van elementen die niet
ondersteund worden, te weten:

* Kop 1 (`#` in Markdown of `<h1>` in HTML)
* Kop 2 (`##` in Markdown of `<h2>` in HTML)
* Kop 5 (`#####` in Markdown of `<h5>` in HTML)
* Kop 6 (`######` in Markdown of `<h6>` in HTML)
* Horizontale regel (`***`, `---` of `___` in Markdown of `<hr>` in HTML)
* Afbeeldingen (`![](image.jpg)` in Markdown of `<img>` in HTML)
* Code (`` `voorbeeld` `` in Markdown of `<code>` in HTML)

Additioneel worden tabellen uit het
[Extended Markdown formaat](https://www.markdownguide.org/extended-syntax/#tables)
ondersteund.

Let op dat "returns" typisch niet als speciale karakters (`\\r\\n`) zichtbaar
zijn in (Markdown) editors maar deze wel nodig zijn in de API.

Bij een veld dat Markdown ondersteund staat dit aangegeven.

## Versies
Productbeschrijvingen kennen versies, die gekenmerkt worden door een bepaalde
publicatiedatum. Bij het ophalen van producten wordt standaard de *actuele*
versie getoond. De actuele versie is de productbeschrijving die op dit moment
geldig is. Het kan echter zijn dat er een concept of een toekomstige versie
aanwezig is maar die is niet zomaar in te zien.

Stel, versie 1 is in het verleden gepubliceerd en heeft publicatiedatum T-2.
Versie 1 was te zien tot versie 2 verscheen op publicatiedatum T-1. Vanaf
publicatiedatum T-1, en ook vandaag (T), is versie 2 te zien. Er is al een
toekomstige versie 3 ingepland, op publicatiedatum T+1. Deze versie 3 is nog
niet op te vragen en versie 2 is dus de actieve versie.

Productbeschrijvingen bijwerken kan leiden tot een nieuwe versie. Hieronder
staan de regels:

* Een publicatiedatum kan niet *voor* een publicatiedatum liggen van een
  eerdere versie.
* Indien de actieve versie publicatiedatum *vandaag* heeft, en er wordt een
  nieuwe versie aangemaakt die ook publicatiedatum *vandaag* heeft, dan zijn er
  2 versies die gepubliceerd zijn op dezelfde dag. In dat geval wordt de versie
  met het hoogste versienummer beschouwd als actief.
* Indien er een versie is met een publicatiedatum in de *toekomst*, en er wordt
  een nieuwe versie aangemaakt, dan overschrijft deze versie de toekomstige
  versie. Er kunnen dus niet meerdere toekomstige versies zijn.
* Indien er geen publicatiedatum wordt opgegeven, dan wordt een concept-versie
  aangemaakt. Een concept-versie wordt altijd overschreven en er kunnen dus
  niet meerdere concept-versies zijn.

Niet actieve versies, zoals oude, toekomstige en concept versies, zijn enkel op
te vragen via historie.

## Proces voor productbeschrijvingen bijwerken

Hoe productbeschrijvingen precies bijgewerkt worden is aan de
integratiespecialist van de organisatie. Hieronder staat een mogelijk scenario:

Het scenario bestaat uit 2 onderdelen:

1. Direct bijwerken in deze API, zodra het product bij de organisatie wijzigt.
2. Dagelijkse (bij voorkeur 's nachts), alle productbeschrijvingen bijwerken
   waar wijzigingen in zijn gemaakt en die nog niet zijn verstuurd naar deze
   API.

We raden aan om een veld bij te houden "laatstVerstuurdAanSDG". U dient dit
veld te voorzien van de actuele datum als een productbeschrijving succesvol is
verstuurd naar deze API. Als u ook een veld "laatstGewijzigd" bijhoudt waarin
de datum wordt opgeslagen waarop de productbeschrijving aan uw kant is
gewijzigd, dan kunt u vergelijkingen maken.

Indien de API niet beschikbaar is, en uw productbeschrijving wijzigt, dan zal
"laatstVerstuurdAanSDG" < "laatstGewijzigd". U kunt dan 's nachts alle
productbeschrijvingen waarvoor dit geldt, alsnog proberen te sturen aan deze
API.

"""

SPECTACULAR_SETTINGS = {
    "TITLE": "PDC API voor producten in de SDG",
    "DESCRIPTION": description,
    "CONTACT": {
        "url": "https://github.com/maykinmedia/sdg-invoervoorziening",
    },
    "LICENSE": {
        "name": "EUPL",
        "url": "https://github.com/maykinmedia/sdg-invoervoorziening/blob/master/LICENSE.md",
    },
    "EXTERNAL_DOCS": {
        "description": "Meer informatie over de SDG",
        "url": "https://www.digitaleoverheid.nl/overzicht-van-alle-onderwerpen/europa/single-digitale-gateway/",
    },
    "VERSION": "1.8.3",
    "SERVE_INCLUDE_SCHEMA": False,
    "CAMELIZE_NAMES": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
}
