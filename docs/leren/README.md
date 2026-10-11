# Leer datamodellering en de route naar Fabric

**Belangrijk:** dit project is nog een startstructuur. Je kunt nu de generator,
SQL-tabellen en voorbeeldqueries bestuderen. Een werkende Fabric-pipeline,
semantisch model en Power BI-rapport zijn nog niet in deze repo aangetoond.

Deze leermap is op 11 oktober 2026 afgestemd op de bestanden. De uitleg over
Fabric-lagen en semantische modellen is gecontroleerd via officiële documentatie.
Een leerplan uitvoeren vraagt aanvullende praktijk; lezen alleen is geen bewijs.

## Je route

1. [Codewandeling en concrete bouwopdrachten](codewandeling.md).
2. [Begrippen: SQL, Python, ETL, modellen en governance](begrippen.md).
3. [Oefeningen met antwoorden](oefeningen.md).
4. [Herhaalkaarten en oefenen met AI](onthouden.md).
5. [Eigen leerlogboek en bewijs](leerlogboek.md).

## Status per onderdeel

| Onderdeel | Huidige staat | Wat nog nodig is |
|---|---|---|
| Synthetische CSV-generator | Python-code aanwezig | Kleine run zelf inspecteren en bronregels controleren |
| Dimensioneel ontwerp | DDL en modeldocument aanwezig | Gegevens laden, relaties controleren en dialect kiezen |
| SQL-analyse | Voorbeeldqueries aanwezig | Zelf resultaat voorspellen en controleren |
| Bronze/Silver/Gold | Beschreven | Werkelijke lagen, transformaties en kwaliteitscontroles |
| Notebooks | Placeholder | Uitvoerbare transformaties met bewijs |
| Fabric-pipelines | Placeholder | Orchestration, foutpad en herstartbewijs |
| dbt | Placeholdermappen | Modellen, configuratie en uitgevoerde controles |
| Power BI / semantisch model | Placeholder | Relaties, measures, rapport en toegangscontrole |
| Tests / CI-CD | Placeholdermappen | Betekenisvolle controles en werkelijke runs |

Een `.gitkeep` bewaart een lege map in Git. Het is geen implementatie.

## Vaardighedenkaart voor de vacature

| Vereiste | Waar beginnen | Bewijs dat je zelf moet opbouwen |
|---|---|---|
| Python | [Generator](../../data-generator/generate_data.py) | Een functie uitleggen en een randgeval onderzoeken |
| SQL | [Queries](../../sql/queries/player_activity.sql) | Grouping, window en duplicaten verklaren |
| Datamodellering | [DDL](../../sql/ddl) en [model](../data-model.md) | Grain, fact/dimension, relaties en historie uitleggen |
| Fabric en ETL | Bouwopdrachten in [codewandeling](codewandeling.md) | Een zelf uitgevoerde bron-naar-gold-route |
| Power BI | Bouwopdracht semantisch model | Zelf gecontroleerde relaties, measures en filters |
| Kwaliteit | Generatorrandgevallen en reconciliatie | Aantallen, totalen en afgekeurde rijen verklaren |
| Governance/security | Bouwopdracht beheer | Eigenaarschap, lineage en geteste toegang |
| Performance | Meetopdracht | Een herhaalbare meting vóór/na een verbetering |
| Stakeholders | KPI-definitie in [leerlogboek](leerlogboek.md) | Vraag vertalen naar toetsbare acceptatie |
| CI/CD | Nog te bouwen | Controle en deployment aantoonbaar uitvoeren |

## Aanbevolen volgorde over je repos

Begin met [Sales Analytics](https://github.com/phlppgdfry/python-data-analytics-project/tree/main/docs/leren)
voor KPI's, ga naar [Mobility ETL](https://github.com/phlppgdfry/belgium-mobility-weather-etl/tree/main/docs/leren)
voor pipelines en sleutels, en gebruik dit project om die ideeën in Fabric te
leren toepassen. Het [Sensorplatform](https://github.com/phlppgdfry/environmental-sensor-data-platform/tree/main/docs/leren)
geeft extra oefening in integraties, normalisatie en kwaliteitsdefinities.

[Terug naar de project-README](../../README.md)
