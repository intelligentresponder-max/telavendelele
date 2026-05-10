"""
searcher.py – Echter Fahrzeug-Suchagent für mobile.de
Kein API-Key nötig. Nutzt öffentliche Suchergebnisse + JSON-LD-Parsing.
"""

import time
import json
import random
import logging
import argparse
import re
from datetime import datetime
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

# ── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("fahrzeug-agent")

# ── Konstanten ───────────────────────────────────────────────
MOBILE_BASE = "https://suchen.mobile.de/fahrzeuge/search.html"
DATA_CACHE  = Path("data/last_results.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Mobile Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ── URL-Builder ──────────────────────────────────────────────
def build_url(profil: dict, region: dict) -> str:
    """Baut die mobile.de-Such-URL aus dem Profil."""
    params = {
        "isSearchRequest": "true",
        "ref": "srp",
        "vc": "Car",
        "zipc": region["plz"],
        "zipr": str(region["umkreis_km"]),
        "ms": f"{profil['mobile_make_id']};{profil['mobile_model_id']};;",
    }

    if "max_preis" in profil:
        params["priceTo"] = str(profil["max_preis"])
    if "min_baujahr" in profil:
        params["minFirstRegistrationDate"] = str(profil["min_baujahr"])
    if "min_ez" in profil:
        params["minFirstRegistrationDate"] = profil["min_ez"][:4]
    if profil.get("nur_haendler"):
        params["dam"] = "0"

    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{MOBILE_BASE}?{query}"


# ── Scraper ──────────────────────────────────────────────────
def hole_inserate(url: str, stichwort: str = None) -> list[dict]:
    """Lädt mobile.de-Suchergebnisse und gibt strukturierte Liste zurück."""
    log.info(f"  → Abrufe URL: {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        log.error(f"  ✗ Verbindungsfehler: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    inserate = []

    # Methode 1: JSON-LD strukturierte Daten
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    ins = item.get("item", {})
                    if ins:
                        inserate.append({
                            "titel":  ins.get("name", ""),
                            "preis":  ins.get("offers", {}).get("price", ""),
                            "url":    ins.get("url", ""),
                            "km":     "",
                            "ez":     "",
                            "quelle": "mobile.de (JSON-LD)",
                        })
        except (json.JSONDecodeError, AttributeError):
            continue

    # Methode 2: HTML-Fallback (Article-Tags)
    if not inserate:
        karten = soup.select("article.caris-ad-tile, div.result-item, div[data-ad-id]")
        for karte in karten:
            titel_el = karte.select_one("h2, .h3-like, .title")
            preis_el = karte.select_one(".price-block, .price, [data-testid='price']")
            link_el  = karte.select_one("a[href]")

            titel = titel_el.get_text(strip=True) if titel_el else ""
            preis = preis_el.get_text(strip=True) if preis_el else ""
            link  = link_el["href"] if link_el else ""

            if not link.startswith("http"):
                link = "https://suchen.mobile.de" + link

            if titel:
                inserate.append({
                    "titel":  titel,
                    "preis":  preis,
                    "url":    link,
                    "km":     "",
                    "ez":     "",
                    "quelle": "mobile.de (HTML)",
                })

    # Methode 3: Meta-Daten aus Seite extrahieren
    if not inserate:
        treffer_text = soup.find(string=re.compile(r"\d+ Angebote|\d+ Fahrzeuge"))
        anzahl = re.search(r"(\d+)", str(treffer_text)).group(1) if treffer_text else "?"
        log.warning(f"  ⚠ Kein Inserat geparst. Seite meldet: {anzahl} Treffer.")
        log.warning("    → Evtl. Blockierung aktiv. Bitte später erneut versuchen.")

    # Stichwort-Filter
    if stichwort and inserate:
        stichwort_lower = stichwort.lower()
        inserate = [i for i in inserate if stichwort_lower in i["titel"].lower()]
        log.info(f"  → Nach Stichwort '{stichwort}': {len(inserate)} Treffer")

    log.info(f"  ✓ {len(inserate)} Inserate gefunden")
    return inserate[:10]  # max 10 pro Profil


# ── Hauptlogik ───────────────────────────────────────────────
def suche_alle_profile(config: dict) -> dict:
    """Durchsucht alle Suchprofile und gibt Ergebnisse zurück."""
    ergebnisse = {}
    region = config["region"]

    for profil in config["suchprofile"]:
        log.info(f"\n🔍 Suche: {profil['bezeichnung']}")
        url = build_url(profil, region)

        inserate = hole_inserate(url, stichwort=profil.get("stichwort"))
        ergebnisse[profil["id"]] = {
            "bezeichnung": profil["bezeichnung"],
            "such_url":    url,
            "zeitpunkt":   datetime.now().isoformat(),
            "inserate":    inserate,
        }

        # Höfliche Pause zwischen Anfragen
        pause = random.uniform(3.0, 6.0)
        log.info(f"  ⏳ Warte {pause:.1f}s ...")
        time.sleep(pause)

    return ergebnisse


# ── Delta-Erkennung ──────────────────────────────────────────
def finde_neue_inserate(aktuell: dict, cache_pfad: Path) -> dict:
    """Vergleicht mit letzten Ergebnissen und gibt nur Neues zurück."""
    if not cache_pfad.exists():
        return aktuell  # Kein Cache → alles ist neu

    with open(cache_pfad) as f:
        alt = json.load(f)

    neu = {}
    for profil_id, daten in aktuell.items():
        alte_urls = {i["url"] for i in alt.get(profil_id, {}).get("inserate", [])}
        neue_inserate = [
            i for i in daten["inserate"]
            if i["url"] not in alte_urls
        ]
        if neue_inserate:
            neu[profil_id] = {**daten, "inserate": neue_inserate}
            log.info(f"  🆕 {len(neue_inserate)} neue Inserate für: {daten['bezeichnung']}")

    return neu


# ── Cache speichern ──────────────────────────────────────────
def speichere_cache(ergebnisse: dict):
    DATA_CACHE.parent.mkdir(exist_ok=True)
    with open(DATA_CACHE, "w", encoding="utf-8") as f:
        json.dump(ergebnisse, f, ensure_ascii=False, indent=2)
    log.info(f"\n💾 Cache gespeichert: {DATA_CACHE}")


# ── Einstieg ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Fahrzeug-Suchagent")
    parser.add_argument("--config",  default="config.yaml", help="Konfigurationsdatei")
    parser.add_argument("--output",  default="bericht.md",  help="Ausgabedatei (Markdown)")
    parser.add_argument("--nur-neu", action="store_true",   help="Nur neue Inserate anzeigen")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    ergebnisse = suche_alle_profile(config)

    if args.nur_neu:
        ergebnisse = finde_neue_inserate(ergebnisse, DATA_CACHE)

    speichere_cache(ergebnisse)

    # Bericht erstellen
    from report_builder import erstelle_bericht
    erstelle_bericht(ergebnisse, config, args.output)
    log.info(f"\n✅ Fertig! Bericht: {args.output}")


if __name__ == "__main__":
    main()
