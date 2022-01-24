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

1. Klik op het tabje **Catalogi** (als u daar nog niet was)
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes (dit kan door bij het 
   kolom huidige informatie te klikken op **Aanpassen**)
5. Klik onderaan op **Opslaan als concept**

Controles na opslaan:

* Detailpagina:
  * Concept producttekst is niet zichtbaar
  * Er wordt een **Melding** getoond dat dit een **concept** producttekst 
  * betreft
  * Bij **Revisies** staat nu dat **versie 1** een **concept** is
* Wijzigen pagina:
  * Concept producttekst is zichtbaar
  * Melding wordt getoond dat dit een concept producttekst betreft
  * Er is geen mogelijkheid om de teksten te vergelijken met standaardteksten

#### 3. Standaard producttekst publiceren als versie 1

1. Klik op het tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes
5. Zorg dat **Product aanwezig** op **Ja** staat
6. Vul een **publicatiedatum** in
7. Klik onderaan op **Opslaan en publiceren**

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

1. Klik op het tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Maak enkele wijzigingen, bij zowel **NL** als **EN** tabjes
5. Vul een **publicatiedatum** in
6. Klik onderaan op **Opslaan en publiceren**

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
4. Om een tweede gemeente te selecteren, klik op **Nog een Role toevoegen**.
5. Selecteer bij deze tweede gemeente, bij **Lokale Overheid**, de gemeente 
   **Zwolle** en vink daarachter **redacteur** aan.
6. Klik op **Opslaan**.

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
6. Je ziet nu de tabjes "Catalogi", "Locaties" en "Gebruikers".
7. Log uit

#### 3. Nogmaals inloggen als gemeentelijke beheerder

1. Ga naar het inlog scherm op ``/``.
2. Vul het e-mailadres en het wachtwoord in, en klik **Inloggen**
3. Je wordt nu gevraagd om een **token**. Vul deze in en klik op **Volgende**
4. Je bent weer ingelogd.

#### 4. Wachtwoord vergeten

1. Ga naar het inlog scherm op ``/``.
2. Klik op **Wachtwoord vergeten**? 
3. Vul je **E-mail** in en klik op **Wachtwoord resetten**

Controles na wachtwoord resetten:

* Er is een e-mail verstuurd naar het opgegeven e-mailadres
* De link in de e-mail komt op de wachtwoord reset pagina terecht

#### 5. Redacteur uitnodigen

* Zorg dat je bent ingelogd als 

1. Ga naar de gemeente *Aalsmeer*
2. Klik op het tabje **Gebruikers**
3. Klik op **Nieuwe gebruiker toevoegen**
4. Vul alle gegevens en vink **Redacteur** aan
5. Klik op **Opslaan**

Controles na opslaan:

* Er is een e-mail verstuurd naar het opgegeven e-mailadres
* De link in de e-mail komt op de pagina om een wachtwoord in te stellen uit

#### 6. Redacteur verwijderen

1. Ga naar de gemeente *Aalsmeer*
2. Klik op het tabje **Gebruikers**
3. Bij **Acties** klik je op **Verwijderen**
4. Klik op **Verwijderen**

#### 7. Locatie informatie invoeren

1. Ga naar de gemeente *Aalsmeer*
2. Klik op het tabje **Loaties**
3. Vul alle velden in 
4. Klik op **Opslaan**

#### 8. Locatie toevoegen

1. Ga naar de gemeente *Aalsmeer*
2. Klik op het tabje **Locaties**
3. Scroll naar beneden
4. Klik op **+ nog een locatie toevoegen**
5. Vul alle velden in 
6. Klik op **Opslaan**

#### 9. Locatie bewerken

1. Ga naar de gemeente *Aalsmeer*
2. Klik op het tabje **Locaties**
3. Scroll naar beneden
4. Klik op **+ nog een locatie toevoegen**
5. Pas de gegevens aan die je wenst aan te passen
6. Klik op **Opslaan**

#### 10. Locatie verwijderen

1. Ga naar de gemeente *Aalsmeer*
2. Klik op het tabje **Locaties**
3. Scroll naar beneden
4. Ga naar **Locatie 1**
5. Klik op **Locatie verwijderen** (de locatie is hiermee nog niet definitief 
   verwijderd)
6. Klik op **Opslaan** (nu is de locatie echt verwijderd)

### GR: Gemeentelijke redacteur

* Zorg dat je eerst **GB-5** hebt gedaan.
* Zorg dat je uitgelogd bent.

#### 1. Inloggen

1. Ga naar ``/`` en login als redacteur die in stap **GB-5** hebt aangemaakt.
2. Je ziet direct de gemeente die bij je account hoort en kan niet kiezen 
   tussen verschillende gemeenten.

#### 2. Producttekst opslaan als concept

1. Klik op het tabje **Catalogi** (als u daar nog niet was)
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes (dit kan door bij het 
   kolom huidige informatie te klikken op **Aanpassen**)
5. Klik onderaan op **Opslaan als concept**

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

1. Klik op het tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Vul overal iets in, bij zowel **NL** als **EN** tabjes
5. Zorg dat **Product aanwezig** op **Ja** staat
6. Vul een **publicatiedatum** in
7. Klik onderaan op **Opslaan en publiceren**

Controles na opslaan:

* Detailpagina:
  * Gepubliceerde producttekst is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Bij **Revisies** staat nu dat **versie 1** gepubliceerd is
* Wijzigen pagina:
  * Gepubliceerde producttekst is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Er is geen mogelijkheid om de teksten te vergelijken met standaardteksten

#### 3. Producttekst later publiceren

1. Klik op het tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op **Wijzigen**
4. Maak enkele wijzigingen, bij zowel **NL** als **EN** tabjes
6. Vul een **publicatiedatum** in, in de toekomst
7. Klik onderaan op **Opslaan en publiceren**

Controles na opslaan:

* Detailpagina:
  * Gepubliceerde producttekst **versie 1** is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Bij **Revisies** staat nu dat **versie 2** gepubliceerd wordt in de toekomst
* Wijzigen pagina:
  * Gepubliceerde producttekst **versie 2** is zichtbaar
  * Er wordt **geen melding** getoond dat dit een concept producttekst betreft
  * Er is geen mogelijkheid om de teksten te vergelijken met standaardteksten

#### 4. Productteksten vergelijken

1. Klik op het tabje **Catalogi**
2. Zoek het product **Parkeervergunning** onder *Diensten*.
3. Klik op het product, en daarna onderaan op Wijzigen
3. Om de productteksten te vergelijken ga je naar bijvoorbeeld **Kosten**
4. Klik op **Vergelijken**
5. Het verschil tussen uw tekst (versie 2, groen) en de standaardtekst 
   (versie 2, rood) wordt getoond.
6. Klik op **Toon standaardtekst**, en klik op het **oog-icoon**
5. Het verschil tussen standaard tekst versie 1 (rood) en 2 (groen) wordt
   getoond.
