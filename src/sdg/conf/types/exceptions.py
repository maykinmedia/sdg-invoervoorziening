from django.core.exceptions import ImproperlyConfigured


class OrganizationTypeException(ImproperlyConfigured):
    """
    Raised when the organization type configuration is invalid.
    """
