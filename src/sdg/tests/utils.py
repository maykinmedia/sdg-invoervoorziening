from django.test import override_settings

disable_2fa = override_settings(TWO_FACTOR_PATCH_ADMIN=False)
