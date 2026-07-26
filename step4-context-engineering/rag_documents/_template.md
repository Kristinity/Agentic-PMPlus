---
# RAG-Dokument-Template für Step 4 (Context Engineering)
#
# Jedes Dokument besteht aus einem YAML-Frontmatter-Block (strukturierte
# Metadaten -> KG-Seite des hybriden KG-Vector-RAG, siehe Quelle #5 in
# step1-feasibility/Benchmark-Analyse.md) und einem Markdown-Body
# (Fließtext -> Vector-Seite, wird gechunkt und embedded).
#
# Kopiere diese Datei, benenne sie sprechend (z. B. sla-becksbrauerei.md)
# und fülle beide Teile aus. Ein Dokument = ein Thema, damit jeder Chunk
# eigenständig eine Frage beantworten kann.

doc_id: "TEMPLATE-001"                # eindeutige ID, referenzierbar aus Logs/Audit-Trail
doc_type: "richtlinie"                # sla | prozessanweisung | produktspezifikation
                                       # | entscheidungsprotokoll | stoerungsbericht | richtlinie
title: "Kurzer, eindeutiger Titel"

# Fuer Filterung/Verknuepfung mit den Step-3-ERP-Tabellen (orders.csv etc.)
kunde: null                           # z. B. "Becksbrauerei" - null falls kundenuebergreifend
produkt: null                         # z. B. "P-KK" - null falls produktuebergreifend
work_center: null                     # z. B. "WC-Presse-KK-02" - null falls nicht maschinenspezifisch

# Aktualitaet: veraltete Richtlinien sind gefaehrlicher als fehlende Docs
gueltig_ab: "2026-01-01"
gueltig_bis: null                     # null = bis auf Widerruf gueltig

# Herkunft/Vertrauen - Voraussetzung fuer kuratierte statt frei erweiterbare
# Wissensquellen (siehe step2-limits/Systemgrenzen.md, Teil C.1: Prompt-
# Injection ueber RAG-Kontext ist eine dort explizit benannte Systemgrenze)
autor: "Name/Rolle, wer dieses Dokument freigegeben hat"
vertrauensstufe: "intern-verifiziert"  # intern-verifiziert | extern-ungeprueft
tags: ["beispiel", "template"]
---

# Kurzer, eindeutiger Titel

Ein bis zwei Saetze Kontext: worum geht es in diesem Dokument, fuer wen/was
ist es relevant.

## Kernaussage

Die eigentliche, chunk-faehige Information - kurz, konkret, in sich
abgeschlossen. Vermeide Verweise wie "siehe oben" oder "wie bereits erwaehnt",
die nur im Volltext, nicht aber in einem isolierten Chunk Sinn ergeben.

## Konsequenz fuer die Planung

Was folgt daraus fuer eine Planungsentscheidung? Diese explizite
Handlungsableitung ist es, was der Agent aus dem RAG-Kontext tatsaechlich
braucht - reine Fakten ohne Handlungsbezug sind fuer die PPS-Entscheidung
oft zu abstrakt.
