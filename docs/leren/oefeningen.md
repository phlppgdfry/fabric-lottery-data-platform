# Fabric en modellering: oefeningen met controleantwoorden

[Leerroute](README.md) · [Codewandeling](codewandeling.md)

Dit zijn denk-, SQL- en bouwopdrachten. De toekomstige Fabric-stappen zijn nog
geen bestaande uitvoerbare pipeline. Open antwoorden pas na je eigen poging.

## 1. Wat is één rij?

Schrijf de grain van `fact_transaction`, `dim_game` en `dim_date` in gewone taal.
Waarom hoort het betaalde bedrag in de fact en niet alleen in het spelrecord?

<details><summary>Antwoord</summary>

Fact: één aankoop/transactie. Game: één huidige spelbeschrijving. Date: één
kalenderdag. Het betaalde bedrag is een historisch feit; een actuele spelprijs
kan later veranderen zonder dat vroegere omzet mag veranderen.

</details>

## 2. Historische omzet bewaken

Er zijn twee aankopen van hetzelfde spel: €5 en €5. De actuele spelprijs wordt
€6. Wat is de historische omzet? Hoe ontstaat de onjuiste uitkomst €12?

<details><summary>Antwoord</summary>

De omzet is **€10**. €12 ontstaat door twee historische aankopen tegen de
huidige dimensieprijs te waarderen. Gebruik de bedragen uit de transacties.
Een goede test wijzigt de dimensieprijs en verwacht ongewijzigde historische omzet.

</details>

## 3. Totaal of cumulatief?

Een speler koopt achtereenvolgens voor €2, €5 en €3. Wat geeft de bestaande
window-som zonder `ORDER BY` op iedere rij? Wat verwacht je bij een cumulatieve som?

<details><summary>Antwoord en SQL-voorbeeld</summary>

Bestaand: **10, 10, 10**. Cumulatief: **2, 7, 10**.

```sql
SELECT transaction_id, player_id, transaction_ts, amount,
       SUM(amount) OVER (
           PARTITION BY player_id
           ORDER BY transaction_ts, transaction_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_spend
FROM fact_transaction;
```

Het extra transactie-ID maakt de volgorde bij gelijke tijden voorspelbaar.
Dit is een leerquery, geen vervanging die al in de bestaande queryfile is aangebracht.

</details>

## 4. Waarom verdwijnen online aankopen?

Een rapport koppelt facts met een inner join aan `dim_location`. Online aankopen
hebben geen locatie. Wat kan er gebeuren en welke keuze moet je maken?

<details><summary>Antwoord</summary>

Die aankopen kunnen uit het resultaat verdwijnen. Gebruik bijvoorbeeld een
left join met een duidelijke niet-retailcategorie, of ontwerp expliciet een
“niet van toepassing”-dimensierij. Maak onderscheid tussen bewust geen locatie
en een ontbrekende locatie die eigenlijk verplicht is. Controleer de omzet vóór
en na de join.

</details>

## 5. Wat bewijst de seed?

Je draait de generator twee keer met dezelfde argumenten en seed. Waarom hoeven
de transactie-ID's niet gelijk te zijn? Waarom is dat relevant voor herladen?

<details><summary>Antwoord</summary>

`random.seed()` bestuurt hier niet `uuid.uuid4()`. De ID's worden opnieuw gemaakt.
Een nieuwe generatie is daardoor niet identiek aan dezelfde bronbatch opnieuw
laden. Voor een idempotentietest moet je dezelfde bewaarde input hergebruiken,
of eerst een expliciet deterministisch sleutelontwerp kiezen.

</details>

## 6. Verdeel regels over datalagen

Waar horen (a) ongewijzigde bron-CSV, (b) getypeerde transactie met gecontroleerde
speler-ID en (c) omzet per dag en kanaal? Wat doe je met een afgekeurde rij?

<details><summary>Antwoord</summary>

a: Bronze. b: Silver. c: Gold. Bewaar de afgekeurde rij of een herleidbare
verwijzing met reden, zodat bron- en doelaantallen verklaarbaar blijven.
Gold mag ook een bruikbaar detailmodel bevatten; “Gold = altijd alleen totalen”
is te beperkt.

</details>

## 7. Een rekencontrole voor je toekomstige rapport

Maak op papier vier transacties: dag 1 online €2 en retail €5; dag 2 online €3
en retail €10. Wat moeten omzet, transactieaantal en gemiddelde waarde tonen
(a) zonder filter en (b) voor alleen online?

<details><summary>Antwoord</summary>

a: **€20, 4 transacties, €5 gemiddeld**. b: **€5, 2 transacties, €2,50 gemiddeld**.
Dag 1 alleen is €7 over twee transacties. Gebruik deze onafhankelijke verwachtingen
om relaties en filtergedrag in het toekomstige model te toetsen.

</details>

## 8. Vind de ontbrekende laadstap

Vergelijk de CSV-kolommen van de generator met de fact-DDL. Waar komt `date_id`
vandaan? Wat gebeurt er als je later transacties buiten de kalenderperiode laadt?

<details><summary>Antwoord</summary>

De generator produceert nog geen `date_id`; een transformatie moet die uit de
transactiedatum afleiden. De bestaande kalender dekt 2023–2025. Buiten die periode
ontbreekt datumcontext, dus moet je de kalender uitbreiden en relaties controleren.
Een genoteerde foreign key is niet hetzelfde als een aangetoonde geldige cloudload.

</details>

## 9. Een bewijslijst bouwen

Welke vijf bewijzen zou je willen tonen voordat je dit een werkende Fabric-route
noemt? Gebruik geen technologie-badges als bewijs.

<details><summary>Mogelijke bewijzen</summary>

1. Bewaarde bronbatch met rijaantallen en herkenbare versie.
2. Uitgevoerde transformatie met verklaarde afkeur en reconciliatie.
3. Werkend facts/dimensies-model met gecontroleerde totalen.
4. Rapport waarvan filters en KPI's met handvoorbeelden overeenkomen.
5. Een gecontroleerde herstart/foutproef plus geteste toegang en runlog.

Bewaar ook uitvoerbare bestanden en benoem welke stappen nog handmatig zijn.

</details>

## 10. Zakelijke wijziging: spelerkenmerken in de tijd

Een speler verandert voorkeurskanaal van retail naar online. De business wil
oude aankopen blijven rapporteren onder het toenmalige voorkeurskanaal.
Waarom is overschrijven van één dimensierij onvoldoende?

<details><summary>Antwoord</summary>

Overschrijven laat het oude kenmerk verdwijnen. Je hebt bijvoorbeeld historische
dimensieversies met geldigheidsperiodes en een verwijzing naar de juiste versie
nodig, of een expliciet vastgelegd kenmerk op het gebeurtenismoment. Het werkelijke
aankoopkanaal in de fact is niet hetzelfde als het voorkeurskanaal van de speler.
Bespreek eerst welke betekenis de gebruiker bedoelt.

</details>

## Eindproef

Leg het stermodel uit, reken een filtervoorbeeld na en benoem minstens drie
onderdelen die nog niet gebouwd zijn. Voer vervolgens één bouwstap uit de
codewandeling echt uit en voeg controlebewijs toe aan het [leerlogboek](leerlogboek.md).
