===============
PDC voor de SDG
===============

:Version: 1.9.3
:Source: https://github.com/maykinmedia/sdg-invoervoorziening
:Keywords: sdg, pdc, gemeenten, provincies, waterschappen, vng, ipo, uvw
:PythonVersion: 3.10

|build-status| |coverage| |docker| |black| |python-versions|

Beheer de teksten van producten en diensten t.b.v. de `Single Digital Gateway`_
(SDG) via het CMS en/of de API.

Ontwikkeld door `Maykin`_ in opdracht van `VNG Realisatie`_ (VNG),
`Interprovinciaal Overleg`_ (IPO) en `Unie van Waterschappen`_ (UVW).


Introductie
===========

De applicatie bestaat uit een CMS en een API. Het CMS stelt redacteuren in
staat productbeschrijvingen direct te beheren, voorbeelden te zien en te
publiceren. De API stelt externe systemen in staat om productbeschrijvingen
geautomatiseerd bij te werken vanuit een eigen CMS. De API is tevens het
centrale punt waar de nationale portalen de productbeschrijvingen ophalen.

Speerpunten zijn (afhankelijk van de installatie en autorisaties):

* Ontzorging: Organisaties hoeven voor de SDG hun eigen website niet aan te
  passen.
* Uniformeren productbeschrijvingen: Het CMS maakt het mogelijk om organisaties
  te ondersteunen met een standaard-productencatalogus.
  Organisaties kunnen een standaard-productbeschrijving overnemen of kunnen
  hiervan afwijken en hun eigen beschrijving maken, zo lang deze aansluit op
  de generieke teksten die met de specifieke teksten worden getoond op de
  nationale portalen.
* Hergebruik van SDG productbeschrijvingen: Teksten die in deze applicatie
  beheerd worden, kunnen ook opgenomen worden in de eigen website via de API.
* Hergebruik van eigen productbeschrijvingen: Teksten die in het CMS van de
  organisatie staan kunnen aangeleverd worden aan de API zodat er geen
  teksten beheerd hoeven te worden via dit CMS.


API specificatie
================

De API specificatie is beschikbaar in het Open API Specification (OAS) versie 3
formaat. De versienummering volgt die van de SDG voorziening als geheel. Indien 
een versie hieronder ontbreekt dan zijn er geen wijzigingen geweest in de API 
specificaties sinds de vorige versie.

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/master/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/master/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.8.3..master#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.8.3           2024-01-30      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.8.3/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.8.3/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.8.3..1.7.2#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.7.2           2023-01-23      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.7.2/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.7.2/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.7.2..1.7.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.7.0           2023-01-06      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.7.0/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.7.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.7.0..1.6.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.6.0           2022-12-14      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.6.0/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.6.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.4.0..1.6.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.4.0           2022-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.4.0/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.4.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.3.0..1.4.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.3.0           2022-08-15      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.3.0/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.3.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.2.0..1.3.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.2.0           2022-05-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.2.0/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.2.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.1.0..1.2.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.1.0           2022-04-08      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1fe65d2e43c37196bbdee161d4fa8951191f7e3a/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1fe65d2e43c37196bbdee161d4fa8951191f7e3a/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.0.0..1fe65d2e43c37196bbdee161d4fa8951191f7e3a#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0           2022-01-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.0.0/src/openapi.yaml&nocors>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.0.0/src/openapi.yaml>`_
==============  ==============  =============================

Zie: `Alle versies en wijzigingen <https://github.com/maykinmedia/sdg-invoervoorziening/blob/master/CHANGELOG.rst>`_


Documentatie
============

Zie ``INSTALL.rst`` voor installatie instructies, beschikbare configuratie
mogelijkheden en commando's.


Links
=====

* `Docker image <https://hub.docker.com/r/maykinmedia/sdg-invoervoorziening>`_
* `Issues <https://github.com/maykinmedia/sdg-invoervoorziening/issues>`_
* `Code <https://github.com/maykinmedia/sdg-invoervoorziening>`_


Licentie
========

Copyright © `Maykin`_ 2021

Licensed under the `EUPL`_.


.. |build-status| image:: https://github.com/maykinmedia/sdg-invoervoorziening/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/sdg-invoervoorziening/actions/workflows/ci.yml

.. |coverage| image:: https://codecov.io/github/maykinmedia/sdg-invoervoorziening/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://app.codecov.io/gh/maykinmedia/sdg-invoervoorziening

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |docker| image:: https://img.shields.io/docker/v/maykinmedia/sdg-invoervoorziening
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/sdg-invoervoorziening

.. |python-versions| image:: https://img.shields.io/badge/python-3.10%2B-blue.svg
    :alt: Supported Python version


.. _`Maykin`: https://www.maykinmedia.nl
.. _`VNG Realisatie`: https://www.vngrealisatie.nl/
.. _`Interprovinciaal Overleg`: https://www.ipo.nl/
.. _`Unie van Waterschappen`: https://unievanwaterschappen.nl/
.. _`Single Digital Gateway`: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2018.295.01.0001.01.ENG&toc=OJ:L:2018:295:TOC
.. _`EUPL`: LICENSE.md
