# Fabric Lottery Data Platform

> **Nederlands leren met deze repo:** [Start de leergids](docs/leren/README.md) — code stap voor stap, vaardigheden, oefeningen met antwoorden, herhaalkaarten en je eigen leerlogboek.
> **Huidige status:** generator en SQL-ontwerp aanwezig; Fabric-pipelines, notebooks, Power BI, dbt en CI/CD zijn nog niet geïmplementeerd. De onderstaande architectuur beschrijft mede het beoogde eindbeeld.

An end-to-end data engineering platform built on Microsoft Fabric, demonstrating:

- Microsoft Fabric (OneLake, Lakehouse, Pipelines, Notebooks)
- Medallion Architecture (Bronze / Silver / Gold)
- PySpark transformations
- SQL & data modelling (star schema)
- dbt (staging → intermediate → marts)
- Fabric Pipelines & orchestration
- Semantic Models & Power BI
- CI/CD (Git integration, deployment pipelines)
- Data quality testing
- Monitoring & production engineering

This project uses **synthetic lottery-style data** (players, games, tickets,
transactions, draws, retail locations, campaigns) — no real personal or
financial data — to build a realistic enterprise-grade data platform end to
end.

## Architecture

```
Source (synthetic events / CSV / API)
              |
        Fabric Pipelines
              |
        BRONZE Lakehouse
           raw data
              |
       PySpark notebooks
              |
        SILVER Lakehouse
      cleaned + validated
              |
          dbt / SQL
              |
          GOLD layer
       business-ready
              |
       Semantic Model
              |
          Power BI
```

Cross-cutting: Git, CI/CD, automated tests, data quality checks, monitoring,
logging, and documented architecture decisions.

## Repository layout

```
architecture/      diagrams and architecture decision records
data-generator/     synthetic data generation (players, games, transactions...)
notebooks/          PySpark notebooks: bronze ingestion, silver transform, gold aggregation
sql/                DDL and reference queries for the data model
dbt/                staging / intermediate / marts models + tests
pipelines/           Fabric pipeline definitions and orchestration notes
tests/              data quality tests
powerbi/            semantic model notes / exports
ci-cd/              CI/CD pipeline definitions (GitHub Actions / Azure DevOps)
docs/               data-model, medallion architecture, performance, monitoring, security
```

## Status

Early scaffold — following a 10-week build plan from fundamentals (SQL, data
modelling) through Fabric, PySpark, dbt, orchestration, CI/CD, and production
engineering (monitoring, security, data quality).

## Why this project exists

Built as a hands-on portfolio project to develop and demonstrate Microsoft
Fabric / Azure data engineering skills: Medallion architecture, distributed
processing with PySpark, data modelling, DataOps, and production-grade
practices (CI/CD, testing, monitoring, security).
