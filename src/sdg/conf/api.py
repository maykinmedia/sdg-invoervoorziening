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
    "PAGE_SIZE": 25,
}

description = f"""
## Introductie
Deze API stelt u in staat om productbeschrijvingen te beheren voor producten
die relevant zijn voor de SDG-verordening.

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
relevante velden in deze API worden aangeduid met `upnLabel` en
`upnIdentificatie`.

Voor organisaties wordt gebruik gemaakt van
[OWMS waardenlijsten](https://standaarden.overheid.nl/owms/4.0/doc/waardelijsten).
De velden in deze API worden aangeduid met `(organisatie)OwmsPrefLabel` en
`(organisatie)OwmsIdentifier`. Afhankelijk van de resource staat het woord
"organisatie" (of iets anders) er wel of niet voor.

Alle objecten worden tevens geïdentificeerd met een
[UUID](https://nl.wikipedia.org/wiki/Universally_unique_identifier). Objecten
die geen Rijksbrede identificatie kennen, hebben enkel een UUID. UUIDs zijn
daarom alleen relevant in gebruik met deze API.

## Ondersteuning voor Markdown
Sommige velden in de API ondersteunen
de basisset van het [Markdown](https://www.markdownguide.org/basic-syntax/)
formaat. Op deze basisset gelden ook nog een aantal uitzonderingen van
elementen die niet ondersteund worden, te weten:

* Kop 1 (`#` in Markdown of `<h1>` in HTML)
* Kop 2 (`##` in Markdown of `<h2>` in HTML)
* Kop 5 (`#####` in Markdown of `<h5>` in HTML)
* Kop 6 (`######` in Markdown of `<h6>` in HTML)
* Horizontale regel (`***`, `---` of `___` in Markdown of `<hr>` in HTML)
* Afbeeldingen (`![](image.jpg)` in Markdown of `<img>` in HTML)
* Code (`` `voorbeeld` `` in Markdown of `<code>` in HTML)

Bij een veld dat Markdown ondersteund staat dit aangegeven.

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
    "VERSION": "1.2.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CAMELIZE_NAMES": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
}
