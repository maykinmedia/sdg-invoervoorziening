==============
Change history
==============

1.9.2
=====

*March 3, 2025*

* Changed broken link detection again: Longer timeout period, no SSL-checking.
* Changed admin to show the URL of a broken link.
* Fixed collapsing of specific texts if an organisation makes a product unavailable.


1.9.1
=====

*February 27, 2025*

* Added broken links view in admin.
* Changed the way broken links are checked. They are now only invalid if a 404 is returned.
* Changed received email option to be enabled by default for new users.
* Changed broken links email text to be more clear.
* Fixed product link in broken links email.


1.9.0
=====

*January 27, 2025*

* [#996] Smaller header and reworked navigation menu
* [#993] Sent periodic mail with broken links
* [#990] Integrated notifications into the menu structure
* [#989] Sort history by date
* [#988] Add ability to change location order
* [#994] Added option for management organization to force push texts
* [#998] Added option for management organization to set products to not be 
  offered by default
* [#987] Remove editor locks
* [#997] Rework the blue edit options in the editor
* [#992] Allow editing Dutch and English in the same screen
* [#991] Clarified some errors in the editor
* [#995] Removed introduction texts and removed info-column from product list
* [#999] Various small tweaks
* Updated all libraries.


1.8.7
=====

*November 1, 2024*

* [#1009] Fixed button shown as disabled on Safari/Chrome inconistantly.


1.8.6
=====

*September 23, 2024*

* [#984] Fixes list bullets properly aligned at the top.
* Consider "xx" and "xX" as placeholders (lowercase Xs).

1.8.5
=====

*May 3, 2024*

* [#981] Fix showing product explanation field-logic.


1.8.4
=====

*February 6, 2024*

* Updated CK-editor


1.8.3
=====

*January 30, 2024*

* [#974] Updated maximum length on procedureLink to 1000 characters.
* Updated dependecies


1.8.2
=====

*September 13, 2023*

* [#967] Clear "toelichting" when product availability is set to unknown or yes.


1.8.1
=====

*June 21, 2023*

* [#963] Added label "decentrale link" in preview page.
* [#964] Improved "decentrale link" validation error messages.


1.8.0
=====

*June 1, 2023*

* [#958] Added placeholder hint for URL-fields
* [#956] Collapse "specifieke tekst" based on "product aanwezig/valt onder" flags.
* [#954] Added popup to warn users about clearing user data
* [#932/#950] Added preview links to national portals.
* [#213] Added email notifications for changed standard texts.
* [#934] Changed existing explanation texts for all relevant products ending in " omdat..." to ".".
* [#929] Removed the posibility to link eu-burger products to eu-bedrijf products (and vice versa).
* [#839] Made the layout for links consistent.
* [#933] Placeholders no longer prevent saving products that are not offered or linked to another product.
* [#786] Set product title to standard text title if empty.
* [#931] Prevent publication of products that have the initial offered status of "unknown".
* [#930] URLs are now validated to start with "https://" to prevent insecure URLs.


1.7.3
=====

*February 16, 2023*

* [#918] Fixed the possibility (data model) to create products with duplicate version numbers via the CMS.
* [#924] Added function to prevent double-clicks on the "save" button in the CMS.
* [#922] Fixed identifying "bevoegde organisaties", in the (create) API, when there are multiple using the same name.
* Added cleanup of obsolete generic product texts to prevent duplicate UUIDs when GT API reuses them.
* Added explanation of the "raadpleger" rol to introduction text in the CMS
* Fixed issue when loading the GT API and some products in the API response lacked the "links"-attribute.
* Fixed "productValtOnder" in the (create) API to only search for products by their "upnUri" within the same doelgroep.


1.7.2
=====

*January 23, 2023*

* Changed product title field to hold upto 150 characters. This is for both the
  CMS as the API.


1.7.1
=====

*January 17, 2023*

* Fixed access to locations in the CMS when products are disabled
* Fixed breadcrumb to show correctly on the organisation page
* Changed invite mail to adhere to organisation style
* Changed error message when providing invalid product-identifying products in API to be more clear.
* Changed sync process to continue when some Logius imports fail
* Fixed incorrect organisation type shown as label in the preview page.


1.7.0
=====

*January 6, 2023*

* [#905] Fixed adding bevoegde organisaties that wasn't functioning in some cases
* [#895] Added preview of concept texts
* [#844] Added command to correct explanation fields that are unmodified from the template
* [#871] Added logic to remove generic products if they are no longer used
* Fixed notifications that were sometimes missing after saving
* Fixed field ordering to match between the CMS and the preview
* Changed that products without a generic text are now visible in the reference catalog
* Changed email addresses to be case-insensitive
* Added "dump" command for product, to generate a full list of all products
* Updated to Python 3.10 and Debian 11 slim image
* Various small changes

**API changes**

* [#847] Added generic product texts resource to the API
* [#824] Remove explanation texts (in the API output) if they are not needed
* Changed product detail and list resources to also show products that have no generic text
* Changed the list of products shown nested in the catalog resource to use the same logic as the product list resource


1.6.1
=====

*December 19, 2022*

* Changed "Het Waterschapshuis" to "Unie van Waterschappen" per request
* Changed error message for issue #856 to be more clear per request
* Visually removed feature #845 (hide products) per request


1.6.0
=====

*December 14, 2022*

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

**API changes**

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
