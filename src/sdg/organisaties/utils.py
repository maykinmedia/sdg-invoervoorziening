from typing import List

from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import LokaleOverheid


def create_specific_catalogs(
    lokale_overheid: LokaleOverheid,
) -> List[ProductenCatalogus]:
    """Create catalogus for all reference catalogus (if it doesn't exist)"""

    catalogus_list = []
    for catalog in ProductenCatalogus.objects.filter(is_referentie_catalogus=True):
        catalogus_list.append(
            ProductenCatalogus(
                referentie_catalogus=catalog,
                lokale_overheid=lokale_overheid,
                is_referentie_catalogus=False,
                domein=catalog.domein,
                versie=catalog.versie,
                naam=catalog.naam,
            )
        )
    return ProductenCatalogus.objects.bulk_create(catalogus_list, ignore_conflicts=True)
