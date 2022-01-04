# Testplan

Dit testplan bevat testscenario's voor het testen van de SDG (Single Digital 
Gateway) invoervoorziening. De SDG is een Europees project om producten 
toegankelijker te maken voor Europese burgers en bedrijven vanuit andere 
landen.

De SDG invoervoorziening is een applicatie voor het beheren van productteksten 
(en niet voor het weergeven van deze teksten anders dan voor beheerdoeleinden).
Deze teksten worden ingevoerd in het Nederlands en in het Engels.

De productteksten zelf zijn bedoeld voor Europese burgers en bedrijven en 
worden via een API aangeleverd aan een aantal zogenaamde Nationale Portalen 
die deze teksten op hun website tonen. De lijst van producten waar deze 
productteksten voor worden geschreven wordt beheerd door Logius, de zogenaamde 
Uniforme Productnamenlijst (UPL). De Nationale Portalen voegen per product een 
generieke tekst toe,

## Doelgroepen en rollen

De SDG invoervoorziening kent 4 type gebruikers, te weten:

* FB: [Functioneel beheerder](./definities.md#Functioneel_beheerder)
* GGR: [Gezamenlijke gemeenteredactie](./definities.md#Gezamenlijke_gemeenteredactie)
* GB: [Gemeentelijke beheerder](./definities.md#Gemeentelijke_beheerder)
* GR: [Gemeentelijke redacteur](./definities.md#Gemeentelijke_redacteur)
* NP: [Nationale Portalen](./definities.md#Nationale_Portalen)

## Start

* We gebruiken **VNG** die de referentie catalogus heeft en de 
  **standaard productteksten**.
* We gebruiken gemeente **Aalsmeer** en **Zwolle** voor testen met 
  **specifieke productteksten** en toegangstesten.
* We gebruiken de producten **Parkeervergunning** en **Identiteitskaart** om
  tests uit te voeren.

### Gebruikers

* ``fb@example.com`` (VNG, Functioneel beheerder)
* ``ggr@example.com`` (VNG, Gezamenlijke gemeenteredactie)

## Testscenario's

### GGR: Gezamenlijke gemeenteredactie

Voor deze scenario's is een account reeds aangemaakt en is het account
toegevoegd aan de VNG organisatie.

#### 1. Login als GGR

1. Ga naar ``/`` en login als ``ggr@example.com``

#### 2. Standaard producttekst opslaan als concept

1. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes
5. Klik onderaan op **Opslaan als concept**

Controles na opslaan:

* Detailpagina:
  * Concept producttekst is niet zichtbaar
  * Er wordt een **Melding** getoond dat dit een **concept** producttekst betreft
  * Bij **Revisies** staat nu dat **versie 1** een **concept** is
* Wijzigen pagina:
  * Concept producttekst is zichtbaar
  * Melding wordt getoond dat dit een concept producttekst betreft
  * Er is geen mogelijkheid om de teksten te vergelijken met standaardteksten

#### 3. Standaard producttekst publiceren als versie 1

1. Klik op tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes
5. Klik onderaan op **Opslaan als concept**

Controles na opslaan:

* Detailpagina:
  * Gepubliceerde producttekst is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Bij **Revisies** staat nu dat **versie 1** gepubliceerd is
* Wijzigen pagina:
  * Gepubliceerde producttekst is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Er is geen mogelijkheid om de teksten te vergelijken met standaardteksten
  
#### 4. Standaard producttekst publiceren als versie 2

1. Klik op tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes
5. Klik onderaan op **Opslaan als concept**

Controles na opslaan:

* Detailpagina:
  * Gepubliceerde producttekst is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Bij **Revisies** staat nu dat **versie 2** gepubliceerd is
* Wijzigen pagina:
  * Gepubliceerde producttekst is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Er is geen mogelijkheid om de teksten te vergelijken met standaardteksten

### FB: Functioneel beheerder

* Zorg dat je uitgelogd bent. 

#### 1. Inloggen

1. Ga naar ``/admin/`` en login als ``fb@example.com``

#### 2. Gemeentelijke beheerder en redacteur uitnodigen

1. Navigeer naar **Accounts** > **Gebruikers** 
2. Klik op **Gebruiker toevoegen** en vul alle gegevens in. 
   Kies een e-mailadres dat je zelf kan raadplegen.
3. Selecteer bij **Lokale Overheid** de gemeente **Aalsmeer**
   vink daarachter **redacteur** en **beheerder** aan.
4. Selecteer bij **Lokale Overheid** de gemeente **Zwolle**
   vink daarachter **redacteur** aan.
5. Klik op **Opslaan**.

### GB: Gemeentelijke beheerder

* Zorg dat je eerst **GGR-4** **FB-2** hebt gedaan.
* Zorg dat je uitgelogd bent.

#### 1. Uitnodiging accepteren

1. Controleer het e-mailadres zoals opgegeven bij **FB-1**.
2. Er is een uitnodigings e-mail met als onderwerp: "Toegang tot de SDG 
   invoervoorziening"
3. Klik op de link in de e-mail.
4. Stel een wachtwoord in

#### 2. Eerste keer inloggen als gemeentelijke beheerder

1. Ga naar het inlog scherm op ``/``.
2. Vul het e-mailadres en het wachtwoord in, en klik **Inloggen**
3. Klik op **Tweestapsauthenticatie instellen** en volg de aanwijzingen
4. Klik uiteindelijk op **Naar de homepage**
5. Je ziet 2 organisaties: **Zwolle** en **Aalsmeer**. Klik op **Aalsmeer**.
6. Je ziet nu de tabjes "Catalogi", "Lokaties" en "Gebruikers".
7. Log uit

#### 3. Nogmaals inloggen als gemeentelijke beheerder

1. Ga naar het inlog scherm op ``/``.
2. Vul het e-mailadres en het wachtwoord in, en klik **Inloggen**
3. Je wordt nu gevraagd om een **token**. Vul deze in en klik op **Volgende**
4. Je bent weer ingelogd.

#### 4. Wachtwoord vergeten

TODO

Check mail, kan resetten, etc.

#### 5. Redacteur uitnodigen

TODO

Bij tabje "Gebruikers" iemand uitnodigen (niet in de admin dus) voor gemeente
alleen gemeente Zwolle.

#### 6. Redacteur verwijderen

TODO

#### 7. Lokatie informatie invoeren

TODO

#### 8. Lokatie toevoegen

TODO

#### 9. Lokatie bewerken

TODO

#### 10. Lokatie verwijderen

TODO

### GR: Gemeentelijke redacteur

* Zorg dat je eerst **GB-5** hebt gedaan.
* Zorg dat je uitgelogd bent.

#### 1. Inloggen

TODO: Zelfde als FB-2 maar met:

5. Je ziet direct de gemeente die bij je account hoort en kan niet kiezen 
   tussen verschillende gemeenten.


#### 2. Producttekst opslaan als concept

TODO

Controles na opslaan:

* Detailpagina:
  * Concept producttekst is niet zichtbaar
  * Er wordt een **Melding** getoond dat dit een **concept** producttekst betreft
  * Bij **Revisies** staat nu dat **versie 1** een **concept** is
* Wijzigen pagina:
  * Concept producttekst is zichtbaar
  * Melding wordt getoond dat dit een concept producttekst betreft
  * Tekst vergelijken met standaard tekst toont verschil tussen de GGR tekst en je eigen tekst.
  * Standaardtekst vergelijken (oog-icoon) toont het verschil tussen **v1** en **v2**.
* API:
  * Producttekst is niet te zien in lijst en detail endpoints
  * Producttekst is wel zichtbaar op product concept endpoint

#### 3. Producttekst nu publiceren

TODO

#### 3. Producttekst later publiceren

TODO

#### 4. Productteksten vergelijken

TODO

#### 5. Historie controleren

TODO

