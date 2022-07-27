==============
Change history
==============

1.3.0
=====

*tbd*

This release introduces changes to the project requested by `IPO`_, making the
project suitable for not only municipalities but also for provinces.

* [#635] Added API autorisations
* [#630] Added writable location API endpoint

.. _`IPO`: https://www.ipo.nl/


1.2.3
=====

*June 30, 2022*

* [#551] Allow indenting bullet lists.
* [#607] Remove search from list product page.
* [#619] Changed location name max length from 40 to 80
* [#606] Changed standard publicatie date to today or future date
* [#450] Disabled submition on enter
* [#540] Added info tool tip to explain the buttons
* [#558] Added ordering numbers
* [#628] Optimized product version query in admin page
* [#610] Changed organisation help text
* [#583] Catch rare case where the UPN is no longer available.
* [#432] Added explanation for save buttons
* [#618] Added notice about lesser menu items when no organisation is selected
* [#565] Changed the column title from "aanwezig" to "aangeboden"
* Fixed tooltips after review.
* Changed tooltip text after review.
* Added CodeQL action


1.2.2
=====

*June 3, 2022*

* [#648] Fixed unwanted whitespacing caused by #641


1.2.1
=====

*June 1, 2022*

* [#644] Fixed the position of the compare labels
* [#642] Fixed the colour of the compare labels
* [#641] Fixed linebreaks to be visable on the preview page


1.2.0
=====

*May 24, 2022*

**API changes**

* The attribute "huisnummer" is now a string.

**CMS changes**

* [#636] Increased invite period to 8 weeks
* [#609] Removed code that was blocking softbreaks
* [#608] Added decentrale procedure link to the _get_specifieke_taal_producten
* [#605] Added function that retrieves value from the translation api
* [#603] Changed huisnummer field in oranisatie model to charfield
* [#600] Added dom elements so the js can detect all organisations
* [#593] Changed empty tests to working tests
* [#588] Added template block tags to show referentie product
* [#585] Added showdown to render the diff elements as markdown
* [#581] Changed str of lokale overheid and organisation to display end date
* [#559] Added standard labels for algemene gegevens
* [#545] Added if statements to check if the input variable has data
* [#543] Added ordering for inforamtiegebieden
* Prevents an infinite loop when cached value is None.
* Prevent removal of default auth org.
* Do not create catalogs for expired orgs.
* Sort products by default.
* Moved bevoegde organisaties in scope of reference products.
* Show "my text" when comparing to my text.
* Moved the toelichtingen fields to be under the pulldowns
* Generic product is now on all products.
* Bevoegde organisatie is mandatory and by default the verantwoordelijke organisatie.
* Removed duplicate tests
* Remove and don't allow zombie products
* Updated all JS en Python packages.
* Updated admin menu


1.1.2
=====

*April 21, 2022*

* [#519] Fixed incorrect lock-icon shown on locations.
* [#534] Fixed bullet styling
* [#557] Fixed admin field config
* [#538, #541] Fixed Firefox issues
* [#553] Added history tab on the edit page
* [#579] Added title and specific texts to preview if provided


1.1.1
=====

*April 20, 2022*

* [#418] Added preview functions
* [#562] Removed unaccessible menu items.
* Various textual changes


1.1.0
=====

*April 8, 2022*

* Revamped the base layout
* Revamped the product list layout
* Revamped the product edit layout
* Changed API spec to be more consistent (AOS version 1.1.0)
* Fixed the way importing themes and information areas works
* Fixed identifying municipalities in the list of government organisations
* Refactored the way filling catalogs with products works
* Various textual changes 
* [#520] Added succesfull messages on submit and delition of the user dropdown menu pages
* [#448] Changed invite mail texts
* [#510] changed max length of title fields from 80 to 100
* [#505] Removed contactnaam
* [#437] Added bevoegde organisaties
* [#472] Limit editor headings
* [#451] Allow collapsing text blocks
* [#446] Import generic product descriptions from the national portals
* [#424] Hide certain fields for reference products
* [#439] Add "product valt onder" fields


1.0.1
=====

*April 1, 2022*

* Updated generic product admin with extra filters and columns.


1.0.0
=====

*January 24, 2022*

* Initial release after 6 sprints, covering the mandatory and many optional
  requirements.
