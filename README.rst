===============
PDC voor de SDG
===============

:Version: 1.5.0
:Source: https://github.com/maykinmedia/sdg-invoervoorziening
:Keywords: vng, ipo, sdg, pdc, gemeenten, provincies
:PythonVersion: 3.8

|build-status| |coverage| |docker| |black| |python-versions|

Beheer de teksten van producten en diensten t.b.v. de `Single Digital Gateway`_
(SDG) via het CMS en/of de API.

Ontwikkeld door `Maykin Media B.V.`_ in opdracht van `VNG Realisatie`_ en 
`IPO`_.


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
  organisatie staan kunnen aangeleverd worden aan de API  zodat er geen
  teksten beheerd hoeven te worden via het CMS.


API specificatie
================

De API specificatie is beschikbaar in het Open API Specification (OAS) versie 3
formaat.

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/master/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/master/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.4.0..master#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.4.0           2022-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.4.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.4.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.3.0..1.4.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.3.0           2022-08-15      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.3.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.3.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.2.0..1.3.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.2.0           2022-05-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.2.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.2.0/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.1.0..1.2.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.1.0           2022-04-08      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1fe65d2e43c37196bbdee161d4fa8951191f7e3a/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1fe65d2e43c37196bbdee161d4fa8951191f7e3a/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.0.0..1fe65d2e43c37196bbdee161d4fa8951191f7e3a#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0           2022-01-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.0.0/src/openapi.yaml>`_,
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

Copyright © `Maykin Media B.V.`_, 2021 - 2022

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

.. |python-versions| image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
    :alt: Supported Python version


.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
.. _`VNG Realisatie`: https://www.vngrealisatie.nl/
.. _`IPO`: https://www.ipo.nl/
.. _`Single Digital Gateway`: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2018.295.01.0001.01.ENG&toc=OJ:L:2018:295:TOC
.. _`EUPL`: LICENSE.md
