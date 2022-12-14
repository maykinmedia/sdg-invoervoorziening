==============
Change history
==============

1.6.0

**December 14, 2022*

* [#838] Fixed preview labels not being translated
* [#868] Fixed crash in rare cases when a known "bevoegde organisatie" was added
* [#854] Removed the "..." suffix from the default reasons
* [#845] Added visibility option to hide products from the national portals
* [#841] Added validation for unchanged "product valt onder toelichting"
* [#843] Added validation for unchanged "product aanwezig toelichting"
* [#856] Added placeholder validation. You can no longer publish texts with "[" or "XX" in them.
* [#827] Added different layout styles for different layers of government.
* Fixed creating a new product version in the admin (although you typically should not do this)
* Added ability to admins to enable concepts/future product publications for API clients

API changes

* [#859] Fixed showing duplicates when going over paginated lists
* [#857] Fixed uncatched error when passing an empty string as catalog
* [#875] Fixed uncatched error when providing an invalid location name
* [#866] Fixed missing location address details for products (they are re-added)
* [#879] Added UUID-attribute to locations
* [#861] Providing an invalid API-token now gives an error instead of continuing as anonymous
* Fixed the product translations-attribute to show as nullable in the API schema
* Fixed the product version-attribute to show up as read-only in the API schema
* Concept products are no longer returned in API responses unless you have write-permission.
* Several major performance improvements


1.5.1
=====

*November 25, 2022*

* [#793] Added webform to preview
* [#837] Moved publication column in product list page to last column
* [#815] Fixed product list in "product valt onder"
* [#846] Fixed missing label configuration
* [#831] Fixed save notifications from not showing up
* [#825] Added `SDG_CMS_PRODUCTS_DISABLED` setting to limit CMS functions
* Fixed issue with detecting proper IP in whitelist
* Various admin improvements
* Added support for water authorities.


1.5.0
=====

*November 10, 2022*

* [#801] Added extra admin fields to filter and sort on
* [#800] Added validation on duplicate name per organisation in the API
* [#751] Added "has costs" field to edit/list pages
* [#799] Added missing lock icon
* [#769] Added periodic task to update status for generic products
* [#576] Added "raadpleger" role
* [#750] Added goatcounter
* [#214] Added notifications page and updated revision list
* [#617] Added sticky toolbox for product editing
* [#770] Added ordering for user model
* [#758] Added localization for preview page
* [#662] Added decentrale procedure label to CMS
* [#819] Excluded products based on generic status
* [#408] Organizations no longer have an enddate by default. 
* [#408] Ensure the API does not return inactive organizations
* [#807] Allow commas in dynamic array fields
* [#576] Fixed edit view and added raadpleger on missing places.
* [#811] How to deal with new/old products
* [#809] Exclude certain generic product status
* [#792] Display information area in product view
* [#808] Textual updates
* [#798] Apply notification improvements
* [#791] Make services fetching more robust to handle DPC API without schema
* [#435] Updated regex for simple HTML detection
* [#484] Ensure logger saves instance name so they are shown when deleted
* [#790] Pass context request for reverse
* [#759] Apply siteconfig and include to templates
* [#785] Ensure proper validation for invitation password
* [#784] Disabled registration / enumeration
* [#671] Updated data loading from services (use `"upnUri"`)
* [#617] Minor styling adjustments
* [#747] Updated text for product-valt-onder
* Create reference product versions if missing
* Fixed several minor security issues
* Added API docs to indicate IM version
* Upgraded libraries


1.4.0
=====

*September 22, 2022*

* [#757] Fixed showing date in message for future publications
* [#742] Fixed bug in the CMS when hosted on a subpath
* [#714] Added command to update English texts with reference texts
* [#399] Added search and filter on otp devices
* [#511] Added product status concept
* [#724] Added correct version control, based on date
* [#622] Changed field label config to be language specific
* [#734] Removed related products entirely
* [#716] Optimized calculation of publication date

**API changes**

* [#732] Fixed API crash when not sending a bevoegdeOrganisatie
* [#723] Fixed bug that crashed the product API endpoint when trying toset verwijzinglinks
* [#722] Added optional IP whitelisting for API access
* [#738] Added a organisation update endpoint for contact details
* [#662] Changed procedureLink to object(label, url)
* [#740] Changed error handeling to match the to NL API strategy
* [#741] Changed error messages to the Dutch language
* [#734] Changed the way to identify locations (by name and URI)
* [#729] Changed the name of certain API fields according to IM 1.6
* [#736] Removed identify based on label


1.3.0
=====

*August 18, 2022*

This release introduces changes to the project requested by `IPO`_, making the
project suitable for not only municipalities but also for provinces.

* [#405] Added servers to (rendered) APIschema
* [#672] Added doelgroep to the duplicate product choices
* [#604] Added field contact formulier link to lokale overheid
* [#637] Changed colour of the i-tag in the CMS
* [#650] Removed empty list option for bevoegde organisatie
* [#621] Improved outlining of preview page
* [#651] Added button to resend mail
* [#692] Added markdown validation
* [#685] Changed list-item styling
* [#683] Added javascript that closes the toelichting on page load when empty
* [#447] Addded styling for the use backup token button

* [#667] Created a landing page for the API on /api.
* [#681] Made doelgroep a required field in the API
* [#691] Added last seen date to API token
* [#660] Changed bevoegde organisatie naam to be unique
* [#669] Created a Postman collection for the supported API calls
* [#668] Added the option to import different data depending on the organization type
* [#666] Allow CMS to be disabled

**API changes**

* [#670] Added (better) documentation in the API schema
* [#722] Added API IP-restrictions
* [#635, #675] Added API autorisations
* [#629] Added writable product API endpoint
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
