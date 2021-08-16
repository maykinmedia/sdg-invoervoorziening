=====================
SDG invoervoorziening
=====================

:Version: 0.1.0
:Source: https://bitbucket.org/maykinmedia/sdg
:Keywords: vng, sdg, pdc
:PythonVersion: 3.8

|build-status| |black| |python-versions|

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

Speerpunten zijn

* Ontzorging: Gemeenten hoeven voor SDG informeren hun website niet aan te 
  passen.
* Uniformeren productbeschrijvingen: Een gedeelde invoervoorziening maakt het 
  mogelijk om gemeenten te ondersteunen met een referentie-productencatalogus. 
  Gemeenten kunnen een referentie-productbeschrijving overnemen of kunnen 
  hiervan afwijken en hun eigen beschrijving maken, zo lang deze aansluit op 
  de generieke teksten die met de specifieke teksten worden getoond op de 
  nationale portalen. 
* Gemeenten beheren SDG content in de invoervoorziening. Gemeenten beheren hun 
  eigen webcontent in hun eigen CMS. d. SDG content wordt bijgehouden ten 
  behoeve van publicatie op de nationale portalen. De gemeente kan de SDG 
  content op haar eigen website en via andere kanalen gebruiken en publiceren, 
  mits ze zelf een API maken die dit mogelijk maakt. Dit is buiten scope van 
  het project zoals beschreven in dit document.


Documentatie
=============

Zie ``INSTALL.rst`` voor installatie instructies, beschikbare configuratie 
mogelijkheden en commando's.


Links
=====

* `Issues <https://taiga.maykinmedia.nl/project/vng-sdg-invoervoorziening>`_
* `Code <https://github.com/maykinmedia/sdg-invoervoorziening>`_

.. |build-status| image:: https://github.com/maykinmedia/sdg-invoervoorziening/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/sdg-invoervoorziening/actions/workflows/ci.yml

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
    :alt: Supported Python version


.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
.. _`VNG Realisatie`: https://www.vngrealisatie.nl/
.. _`Single Digital Gateway`: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2018.295.01.0001.01.ENG&toc=OJ:L:2018:295:TOC
