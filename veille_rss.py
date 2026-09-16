#!/usr/bin/env python3
"""
Pipeline de veille passive - v0 (test bout en bout)
Source RSS -> récupération -> qualification -> fichier central (CSV + JSON)

Usage :
  python3 veille_rss.py                    # récupère les flux définis dans SOURCES
  python3 veille_rss.py fichier.xml        # mode test : parse un fichier RSS local

Sortie :
  veille.csv  : base centrale (ouvrable dans Sheets / importable ClickUp)
  veille.json : même contenu en JSON (pour brancher n8n/Make/ClickUp API plus tard)
  seen.json   : liens déjà vus (déduplication entre deux exécutions)

"""

import csv
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

# ---------------------------------------------------------------- config

SOURCES = [
    {"name": "ActuIA", "url": "https://www.actuia.com/feed/"},
    # Ajouter d'autres sources ici, ex :
    # {"name": "Numerama", "url": "https://www.numerama.com/feed/"},
]

# Mots-clés -> thème. Le premier thème qui matche gagne.
THEMES = {
    "Cybersécurité":        ["faille", "vulnérabilité", "cve", "kev", "ransomware", "cyberattaque", "sécurité"],
    "Régulation / éthique": ["ai act", "rgpd", "régulation", "cnil", "loi", "éthique", "gouvernance"],
    "Modèles & produits IA": ["gpt", "claude", "mistral", "gemini", "llama", "modèle", "agent"],
    "Business / marché":    ["lève", "levée", "rachat", "acquisition", "valorisation", "investissement", "milliard"],
    "Infrastructure":       ["datacenter", "gpu", "puce", "nvidia", "cloud", "supercalculateur"],
}

# Mots-clés qui augmentent la pertinence pour Actu Tech (à adapter au projet)
PERTINENCE_HAUTE = ["ia", "intelligence artificielle", "cyber", "faille", "mistral", "openai", "anthropic", "google"]
PERTINENCE_MOYENNE = ["cloud", "startup", "levée", "régulation"]

STATUT_INITIAL = "À lire"   # workflow : À lire -> Pertinent -> À décrypter -> Rejeté

OUT_DIR = Path(__file__).parent
CSV_PATH = OUT_DIR / "veille.csv"
JSON_PATH = OUT_DIR / "veille.json"
SEEN_PATH = OUT_DIR / "seen.json"

FIELDS = ["titre", "lien", "source", "date", "theme", "resume", "pertinence", "statut"]

# ---------------------------------------------------------------- fonctions

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "VeillePassive/0.1 (test EJP Tech)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def qualify_theme(text: str) -> str:
    low = text.lower()
    for theme, kws in THEMES.items():
        if any(k in low for k in kws):
            return theme
    return "Autre / à qualifier"


def qualify_pertinence(text: str) -> str:
    low = text.lower()
    if any(k in low for k in PERTINENCE_HAUTE):
        return "Haute"
    if any(k in low for k in PERTINENCE_MOYENNE):
        return "Moyenne"
    return "Basse"


def parse_rss(xml_bytes: bytes, source_name: str) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    records = []
    for item in root.iter("item"):
        titre = clean(item.findtext("title", ""))
        lien = clean(item.findtext("link", ""))
        resume = clean(item.findtext("description", ""))[:300]
        raw_date = item.findtext("pubDate", "")
        try:
            date = parsedate_to_datetime(raw_date).strftime("%Y-%m-%d")
        except Exception:
            date = raw_date or datetime.now().strftime("%Y-%m-%d")
        blob = f"{titre} {resume}"
        records.append({
            "titre": titre,
            "lien": lien,
            "source": source_name,
            "date": date,
            "theme": qualify_theme(blob),
            "resume": resume,
            "pertinence": qualify_pertinence(blob),
            "statut": STATUT_INITIAL,
        })
    return records


def load_seen() -> set:
    if SEEN_PATH.exists():
        return set(json.loads(SEEN_PATH.read_text()))
    return set()


def save_central(new_records: list[dict]) -> None:
    existing = json.loads(JSON_PATH.read_text()) if JSON_PATH.exists() else []
    existing.extend(new_records)
    JSON_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(existing)


# ---------------------------------------------------------------- main

def main():
    seen = load_seen()
    new_records = []

    if len(sys.argv) > 1:  # mode test fichier local
        xml_bytes = Path(sys.argv[1]).read_bytes()
        new_records = [r for r in parse_rss(xml_bytes, "ActuIA (test local)") if r["lien"] not in seen]
    else:
        for src in SOURCES:
            try:
                xml_bytes = fetch(src["url"])
                new_records += [r for r in parse_rss(xml_bytes, src["name"]) if r["lien"] not in seen]
            except Exception as e:
                print(f"[ERREUR] {src['name']} : {e}")

    if not new_records:
        print("Aucun nouvel article.")
        return

    save_central(new_records)
    seen.update(r["lien"] for r in new_records)
    SEEN_PATH.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2))

    print(f"{len(new_records)} nouvel(s) article(s) ajouté(s) :")
    for r in new_records:
        print(f"  [{r['pertinence']:^7}] {r['theme']} | {r['titre'][:70]}")


if __name__ == "__main__":
    main()
