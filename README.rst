=====================
SDG invoervoorziening
=====================

:Version: latest
:Source: https://github.com/maykinmedia/sdg-invoervoorziening
:Keywords: vng, sdg, pdc
:PythonVersion: 3.8

|build-status| |coverage| |docker| |black| |python-versions|

Beheer de teksten van producten en diensten t.b.v. de `Single Digital Gateway`_
(SDG).

Ontwikkeld door `Maykin Media B.V.`_ in opdracht van `VNG Realisatie`_.


Introductie
===========

De SDG invoervoorziening is een applicatie voor het beheren en ontsluiten van 
SDG productbeschrijvingen van gemeenten. Deze productomschrijvingen worden 
ontsloten via een API. 

Gemeenten kunnen een referentie-productbeschrijving overnemen of kunnen hiervan 
afwijken en hun eigen beschrijving maken.

Speerpunten zijn:

* Ontzorging: Gemeenten hoeven voor SDG informeren hun website niet aan te 
  passen.
* Uniformeren productbeschrijvingen: Een gedeelde invoervoorziening maakt het 
  mogelijk om gemeenten te ondersteunen met een referentie-productencatalogus. 
  Gemeenten kunnen een referentie-productbeschrijving overnemen of kunnen 
  hiervan afwijken en hun eigen beschrijving maken, zo lang deze aansluit op 
  de generieke teksten die met de specifieke teksten worden getoond op de 
  nationale portalen. 
* Gemeenten beheren SDG content in de invoervoorziening. Gemeenten beheren hun 
  eigen webcontent in hun eigen CMS. De SDG content wordt bijgehouden ten 
  behoeve van publicatie op de nationale portalen. De gemeente kan de SDG 
  content op haar eigen website en via andere kanalen gebruiken en publiceren, 
  mits ze zelf een API maken die dit mogelijk maakt (dit laatste is buiten 
  scope van het project).


API specificatie
================

De API specificatie is beschikbaar in het Open API Specification (OAS) versie 3
formaat.

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/master/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/master/src/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/sdg-invoervoorziening/compare/1.0.0..master#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0           2022-01-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.0.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/sdg-invoervoorziening/1.0.0/src/openapi.yaml>`_

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

Copyright © `VNG Realisatie`_, 2021 - 2022

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
.. _`Single Digital Gateway`: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2018.295.01.0001.01.ENG&toc=OJ:L:2018:295:TOC
.. _`EUPL`: LICENSE.md
