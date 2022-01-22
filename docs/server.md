# Server vereisten

De SDG invoervoorziening bestaat uit minimaal 3 Docker containers, een database
(PostreSQL), cache-server (Redis) en webserver (Nginx) of loadbalancer
(Traefik).

Voor de server vereisten van de SDG invoervoorziening zijn parameters 
opgesteld, performance metingen gedaan en vervolgens de vereisten opgesteld om
aan de parameters te voldoen.

## Parameters

**Snelheid**

* Het laden van een pagina duurt maximaal 2 seconden
* Het opslaan van een doorgevoerde wijziging duurt maximaal 3 seconden

**Capaciteit**

* 100 web-redacteuren moeten tegelijkertijd kunnen (concurrent) werken in de 
  invoervoorziening
* Het aantal van 100 is gebaseerd op de aanname dat maximaal 10% van de 352 
  gemeentelijke web-redacties tegelijkertijd in de invoervoorziening aan de 
  slag is. Van de gemeentelijke web-redactie werken er 3 redacteuren aan de 
  productbeschrijvingen.
* Nominaal zijn er naar schatting 20 redacteuren aan het werk in de 
  invoervoorziening wanneer er geen landelijke wijzigingen op stapel staan
* Minimaal aantal te beheren productbeschrijvingen is 35.000
* Naar beneden afgerond 100 producten x 352 gemeenten = 35.200 
  productbeschrijvingen
* Ieder product kent per gemeente een Nederlandstalige- en een Engelstalige 
  beschrijving.
* Het aantal producten gaat in de loop van de tijd groeien. De 
  invoervoorziening start met de SDG shortlist (35 producten), vervolgens de 
  longlist (bijna 100) en gaat mogelijk doorgroeien naar alle gemeentelijke 
  producten (volgens UPL ongeveer 400).

## Server vereisten

Op basis van bovenstaande parameters zijn performance metingen gedaan en zijn
de volgende minimal server vereisten opgesteld:

* Platform: 64-bit
* Processor(s): 8 CPUs (cores) @ 2.0 GHz
* Geheugen: 32 GB
* Schijfruimte: 30 GB

Typische container setup:

* 1 tot 3 applicatie replicas/containers
* 2 achtergrond taken (Celery worker) replicas/containers
* 1 cron taak (Celery beat)
