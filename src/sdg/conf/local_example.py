#
# Any machine specific settings when using development settings.
#
import os

os.environ.setdefault("TWO_FACTOR_PATCH_ADMIN", "no")
os.environ.setdefault("TWO_FACTOR_FORCE_OTP_ADMIN", "no")


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sdg",
        "USER": "sdg",
        "PASSWORD": "sdg",
        "HOST": "localhost",  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        "PORT": 5432,  # Set to empty string for default.
    }
}
