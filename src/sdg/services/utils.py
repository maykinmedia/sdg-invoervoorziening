from typing import Dict, List


def retrieve_service_data() -> List[Dict]:
    """
    Retrieve data from all available services.
    """
    from sdg.services.models import ServiceConfiguration

    data = []
    for service_config in ServiceConfiguration.objects.all():
        data.extend(service_config.retrieve_products())

    return data
