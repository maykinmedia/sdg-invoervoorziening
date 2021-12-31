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

* [Functioneel beheerder](./definities.md#Functioneel_beheerder)
* [Gemeentelijke beheerder](./definities.md#Gemeentelijke_beheerder)
* [Gemeentelijke redacteur](./definities.md#Gemeentelijke_redacteur)
* [Nationale Portalen](./definities.md#Nationale_Portalen)

## Testscenario's

### Functioneel beheerder (FB)

#### 1. Inloggen

1. Ga naar `/admin/` en login als functioneel beheerder

#### 2. Gemeentelijke beheerder uitnodigen

1. Navigeer naar **Accounts** > **Gebruikers** 
2. Klik op **Gebruiker toevoegen** en vul alle gegevens in. 
   Kies een e-mailadres dat je zelf kan raadplegen.
3. Selecteer bij **Lokale Overheid** een nog niet eerder gekozen gemeente en 
   vink daarachter **beheerder** aan.
4. Klik op **Opslaan**.


### Gemeentelijke beheerder (GB)

Zorg dat je uitgelogd bent.

#### 1. Uitnodiging accepteren

Doe eerst **FB-1**.

1. Controleer het e-mailadres zoals opgegeven bij **FB-1**.
2. Er is een uitnodigings e-mail met als onderwerp: "Toegang tot de SDG 
   invoervoorziening"
3. Klik op de link in de e-mail.
4. Stel een wachtwoord in

#### 2. Eerste keer inloggen als gemeentelijke beheerder

1. Ga naar het inlog scherm op `/`.
2. Vul het e-mailadres en het wachtwoord in, en klik **Inloggen**
3. Klik op **Tweestapsauthenticatie instellen** en volg de aanwijzingen
4. Klik uiteindelijk op **Naar de homepage**
5. Je ziet direct de gemeente die bij je account hoort en kan niet kiezen 
   tussen verschillende gemeenten.
6. Je zie tevens de tabjes "Catalogi", "Lokaties" en "Gebruikers".
7. Log uit

#### 3. Nogmaals inloggen als gemeentelijke beheerder

1. Ga naar het inlog scherm op `/`.
2. Vul het e-mailadres en het wachtwoord in, en klik **Inloggen**
3. Je wordt nu gevraagd om een token. Vul deze in en klik op **Volgende**
4. Je bent weer ingelogd.

#### 4. Wachtwoord vergeten

TODO vanaf hier

Check mail, kan resetten, etc.

#### 5. Redacteur uitnodigen

Bij Gebruikers iemand uitnodigen (niet in de admin)

#### 6. Redacteur verwijderen

#### 7. Lokatie informatie invoeren

#### 8. Lokatie toevoegen

#### 9. Lokatie bewerken

#### 10. Lokatie verwijderen


### Gemeentelijke redacteur (GR)

Doe eerst **GB-5**.

#### 1. Inloggen

#### 2. Producttekst opslaan als concept

#### 3. Producttekst nu publiceren

#### 4. Productteksten vergelijken

#### 5. Historie controleren

