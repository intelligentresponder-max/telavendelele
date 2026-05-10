"""
report_builder.py – Erstellt Markdown-Bericht + WhatsApp-Vorlage
"""

from datetime import datetime
from pathlib import Path


def erstelle_bericht(ergebnisse: dict, config: dict, ausgabe_pfad: str):
    """Schreibt vollständigen Markdown-Bericht."""
    datum = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
    zeilen = []

    zeilen.append(f"# 🚗 Fahrzeug-Suchabericht")
    zeilen.append(f"**Erstellt:** {datum}  ")
    zeilen.append(f"**Region:** PLZ {config['region']['plz']}, Umkreis {config['region']['umkreis_km']} km\n")
    zeilen.append("---\n")

    # ── Suchergebnisse ───────────────────────────────────────
    gesamt_inserate = 0

    for profil_id, daten in ergebnisse.items():
        inserate = daten.get("inserate", [])
        gesamt_inserate += len(inserate)

        zeilen.append(f"## 🔍 {daten['bezeichnung']}")
        zeilen.append(f"**Gefunden:** {len(inserate)} Inserate  ")
        zeilen.append(f"**Suchlink:** [{daten['such_url'][:60]}...]({daten['such_url']})\n")

        if not inserate:
            zeilen.append("_Keine Treffer oder Seite nicht auswertbar._\n")
        else:
            for i, ins in enumerate(inserate, 1):
                preis = f"**{ins['preis']} €**" if ins.get("preis") else "_Preis auf Anfrage_"
                zeilen.append(f"### {i}. {ins['titel']}")
                zeilen.append(f"- Preis: {preis}")
                if ins.get("km"):
                    zeilen.append(f"- Kilometerstand: {ins['km']}")
                if ins.get("ez"):
                    zeilen.append(f"- Erstzulassung: {ins['ez']}")
                zeilen.append(f"- Quelle: {ins.get('quelle', 'mobile.de')}")
                if ins.get("url"):
                    zeilen.append(f"- [→ Zum Inserat]({ins['url']})")
                zeilen.append("")

        zeilen.append("---\n")

    # ── Händlerliste ─────────────────────────────────────────
    zeilen.append("## 🏢 Händler im Rhein-Main-Gebiet")
    zeilen.append("*Direkte Kontakte für Verhandlungen und Verfügbarkeitsanfragen:*\n")

    for h in config.get("haendler_kontakte", []):
        zeilen.append(f"### {h['name']}")
        zeilen.append(f"- 📍 {h.get('adresse', '')}")
        if h.get("telefon"):
            zeilen.append(f"- 📞 {h['telefon']}")
        if h.get("email"):
            zeilen.append(f"- ✉️ {h['email']}")
        if h.get("web"):
            zeilen.append(f"- 🌐 {h['web']}")
        if h.get("ansprechpartner"):
            zeilen.append(f"- 👤 {h['ansprechpartner']}")
            if h.get("ansprechpartner_email"):
                zeilen.append(f"  - {h['ansprechpartner_email']}")
        marken = ", ".join(h.get("marken", []))
        zeilen.append(f"- 🏷️ Marken: {marken}")
        zeilen.append("")

    zeilen.append("---\n")
    zeilen.append(f"**Gesamt gefundene Inserate:** {gesamt_inserate}  ")
    zeilen.append("*Automatisch erstellt vom Fahrzeug-Suchagenten.*")

    # Datei schreiben
    Path(ausgabe_pfad).parent.mkdir(parents=True, exist_ok=True)
    with open(ausgabe_pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen))

    # WhatsApp-Vorlage generieren
    erstelle_whatsapp_vorlage(ergebnisse, config)


def erstelle_whatsapp_vorlage(ergebnisse: dict, config: dict):
    """Erstellt kopierfertige WhatsApp-Nachricht."""
    datum = datetime.now().strftime("%d.%m.%Y")
    vorlage_pfad = config.get("benachrichtigung", {}).get(
        "whatsapp_vorlage", "src/templates/whatsapp_nachricht.txt"
    )

    zeilen = [
        f"🚗 *Fahrzeug-Update {datum}*",
        f"Region: {config['region']['plz']} | Umkreis: {config['region']['umkreis_km']} km\n",
    ]

    for daten in ergebnisse.values():
        inserate = daten.get("inserate", [])
        if not inserate:
            continue
        zeilen.append(f"*{daten['bezeichnung']}* → {len(inserate)} Treffer")
        for ins in inserate[:3]:
            preis = ins.get("preis", "?")
            preis_str = f"{preis} €" if preis else "Preis auf Anfrage"
            zeilen.append(f"  • {ins['titel'][:45]} – {preis_str}")
        zeilen.append("")

    zeilen.append("📋 Vollständiger Bericht im GitHub-Repo verfügbar.")
    zeilen.append("_(Automatisch erstellt)_")

    Path(vorlage_pfad).parent.mkdir(parents=True, exist_ok=True)
    with open(vorlage_pfad, "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen))

    print(f"📱 WhatsApp-Vorlage: {vorlage_pfad}")
