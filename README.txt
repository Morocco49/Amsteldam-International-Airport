AMSTELDAM INTERNATIONAL AIRPORT — LIVE DEPARTURES
=================================================

Wat zit erin?
- Groot vertrekbord met extra grote, dikke letters en fullscreen.
- Echte vertrekkende vluchtgegevens uit de Schiphol PublicFlight API.
- Automatische gegevensupdate elke 60 seconden.
- Taalwisseling NL → EN → FR → Chinees, elke 10 seconden.
- De klok loopt live.
- De Client Secret blijft in config.json op je eigen apparaat; de browser krijgt deze nooit.

BELANGRIJK
Amsteldam is de naam van het ontwerp. De echte vluchtgegevens komen van Amsterdam Airport Schiphol.
Je hebt een eigen Schiphol Developer Portal-account en goedgekeurde toegang tot de PublicFlight API nodig.
Zonder die toegang kan de app geen echte vluchtdata tonen.

EERST API-TOEGANG REGELEN
1. Ga naar https://developer.schiphol.nl/
2. Maak een account aan en registreer een Application.
3. Abonneer de Application op de Schiphol PublicFlight API en wacht op eventuele goedkeuring.
4. Bewaar de Client ID en Client Secret veilig. Deel ze met niemand.
5. Open config.example.json en maak daarvan een kopie met de naam config.json.
6. Vul alleen in config.json je Client ID en Client Secret in.

STARTEN OP EEN CHROMEBOOK
1. Sla de ZIP op en pak hem uit in je map Downloads.
2. Chromebook: Instellingen → Geavanceerd → Ontwikkelaars → Linux-ontwikkelomgeving inschakelen.
3. Open de Linux Terminal.
4. Ga naar de uitgepakte map. Als die in Downloads staat, kopieer hem eerst naar Linux-bestanden via de Bestanden-app.
5. In Terminal typ je:
   cd amsteldam_airport_live
   python3 server.py
6. Open Chrome en ga naar:
   http://127.0.0.1:8000
7. Klik op Volledig scherm.

STOPPEN
Ga terug naar Terminal en druk Ctrl+C.

VEILIGHEID
- Deel config.json nooit en zet hem niet online.
- Zet je Client Secret nooit in index.html.
- De server luistert alleen op 127.0.0.1 (alleen deze Chromebook).
- Dit pakket bevat geen geheime sleutels en kan dus niet zonder jouw API-toegang live data ophalen.

OPMERKING OVER VELDEN
Gate of status kan door Schiphol leeg worden gelaten zolang die informatie nog niet bekend is.
Het bord toont dan — in plaats van gegevens te verzinnen.
