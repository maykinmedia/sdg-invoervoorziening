#
# Any machine specific settings when using development settings.
#

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sdg-acc",
        "USER": "sdg",
        "PASSWORD": "sdg",
        "HOST": "",  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        "PORT": "",  # Set to empty string for default.
    }
}

# from .dev import REST_FRAMEWORK

# REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
#     "rest_framework.renderers.BrowsableAPIRenderer"
# )
LOGGING = None
