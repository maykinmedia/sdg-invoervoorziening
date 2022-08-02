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

description = """
# Introductie:
De SDG invoervoorziening is een applicatie voor het beheren en ontsluiten van
productbeschrijvingen van producten die worden aangeboden door organisaties in de
overheidsorganisaties. Deze producten vallen onder de SDG verordening en de
productbeschrijvingen worden ontsloten via een API.

# Autorisatie
De API maakt gebruik van een API-Token. Met deze token kunt u toegang krijgen voor de
lees-schrijf API calls per organisatie. De API-Token wordt via de header doorgegeven en ziet er
uit als volgt: `Authorization: Token <token>`. Deze token is dus alleen nodig wanneer u
een `POST`, `PUT` of een `DELETE` call maakt. Voor `GET` calls heeft u geen API-Token nodig.
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "SDG Invoervoorziening API",
    "DESCRIPTION": description,
    "CONTACT": {
        "url": "https://github.com/maykinmedia/sdg-invoervoorziening",
    },
    "LICENSE": {
        "name": "EUPL-1.2",
        "url": "https://github.com/maykinmedia/sdg-invoervoorziening/blob/master/LICENSE.md",
    },
    "EXTERNAL_DOCS": {
        "description": "Extra informatie over de SDG Invoervoorziening",
        "url": "https://vng.nl/projecten/single-digital-gateway",
    },
    "VERSION": "1.2.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CAMELIZE_NAMES": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
}
