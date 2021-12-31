# Functioneel beheer

Het functioneel beheer wordt uitgevoerd door VNG en bestaat uit een aantal veel
voorkomende handmatige acties.

## Handmatige acties

### Controleren van gemeenten zonder gemeentelijke beheerder

Een gemeente kan alleen haar specifieke productteksten beheren als ter minste 1
gemeentelijke beheerder is aangesteld voor die gemeente. Dit is eenvoudig te
controleren in de SDG invoervoorziening.

1. Navigeer naar **Organisaties** > **Lokale overheden**

2. Filter de lijst op **Beheerder: Nee**

3. Het resultaat is een lijst van alle gemeenten zonder beheerder.

### Gemeentelijke beheerder uitnodigen

Een gemeentelijke beheerder neemt contact op met VNG om toegang te verkrijgen 
tot de SDG invoervoorziening. De functioneel beheerder het verzoek verifieren 
en kan de gemeentelijke beheerder uitnodigen.

1. Navigeer naar **Accounts** > **Gebruikers** 

2. Klik op **Gebruiker toevoegen** en vul alle gegevens in:

   * **E-mailadres**: Het e-mailadres waarop de gemeentelijke beheerder een 
     uitnodiging ontvangt om in te loggen op de SDG invoervoorziening.
   * **Voornaam**: De voornaam van de gemeentelijke beheerder.
   * **Achternaam**: De achternaam, inclusief tussenvoegsels, van de 
     gemeentelijke beheerder.

3. Selecteer bij **Lokale Overheid** de juiste gemeente(n) en vink daarachter
   **beheerder** aan.

4. Klik op **Opslaan**. Hoewel het detail scherm opent is meer informatie niet
   nodig.

### Catalogi omzetten als een gemeenten samenvoegt of splitst

Als een gemeente samenvoegt of splitst, komt dat tot uiting in nieuwe lokale
overheden die beschikbaar komen (de oude krijgt een einddatum).

De catalogi van de oude gemeente kan omgehangen worden naar de nieuwe gemeente.

1. Navigeer naar **Catalogi** > **Producten catalogi**

2. Kies de juiste catalogus en klik op de **naam**

3. In het detail scherm, selecteer bij **Lokale overheid** de juiste/nieuwe
   lokale overheid om de catalogus te verplaatsen naar deze gemeente.

### Tweestapsauthenticatie herstellen

Als functioneel beheerder kunt u de tweestapsauthenticatie van een andere 
gebruiker opnieuw instellen.

1. Navigeer naar **Accounts** > **TOTP devices**.

2. Vink het checkbox aan in de lijst van het betreffende account.

3. Kies bij **Actie** de optie **Verwijder geselecteerde TOTP devices** en 
   klik op de knop **Uitvoeren**.

4. Op de bevestigingspagina klikt u op **Ja, ik weet het zeker**.

De gebruiker van het betreffende account krijgt nu bij inloggen de mogelijkheid
om opnieuw de QR code te scannen en tweestapsauthenticatie in te stellen.

### Toegang geven tot de API

Hoewel de API publiekelijk toegankelijk is kunnen gebruikers met een API-token
ongelimiteert gebruik maken van de API waar gebruikers zonder API-token wel
gelimiteert worden (100 verzoeken per minuut).

1. Navigeer naar **API** > **Tokens**.

2. Klik op **Token toevoegen** en vul alle gegevens in.

3. Klik op **Opslaan en opnieuw bewerken**, en het **Sleutel** veld wordt 
   ingevuld.

Stuur de waarde van het **Sleutel** veld op naar de gebruiker die van de API 
gebruik gaat maken. Deze sleutel wordt ook wel API-token genoemd. De 
API specificatie geeft aan hoe dit token gebruikt kan worden.

## Automatische taken

### Inladen van door Logius beheerde tabellen

Dagelijks rond 1:00 (UTC) worden de volgende lijsten bijgewerkt op basis van
de bron op **standaarden.overheid.nl**:

* Gemeenten (https://standaarden.overheid.nl/owms/terms/Gemeente.xml)
* UPL (https://standaarden.overheid.nl/owms/oquery/UPL-actueel.csv)
* SDG-informatiegebieden (https://standaarden.overheid.nl/owms/oquery/SDG-Informatiegebieden.csv)
* UPL-SDG-informatiegebieden (https://standaarden.overheid.nl/owms/oquery/UPL-SDG-Informatiegebied.csv)

Nieuwe objecten worden toegevoegd en bestaande objecten worden bijgewerkt. Het
kan hierdoor zijn dat een gemeente een einddatum krijgt als deze is opgeheven.

### Aanmaken van (nieuwe) generieke producttekst placeholders

Dagelijks rond 2:00 (UTC) worden nieuwe generieke producttekst placeholders
aangemaakt op basis van de UPL. Zo'n placeholder is niets meer dan een lege
generieke producttekst die later \* gevuld wordt door de Nationale Portalen.

Catalogi die in aanmerking komen om automatisch gevuld te worden, worden tevens
voorzien van een specieke producttekst placeholder. Deze platholder is wederom
niets meer dan een lege specifieke producttekst, die bedoeld is om door de GGR
te voorzien van standaardteksten via de SDG invoervoorziening.

\* Deze feature is op het moment van schrijven nog niet geïplementeerd door het
ontbreken van een API van de Nationale Portalen.

### Opschonen van logs

Dagelijks rond 4:00 (UTC) worden allerhande log-bestanden opgeschoond waar 
nodig.
