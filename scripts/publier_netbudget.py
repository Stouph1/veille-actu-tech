#!/usr/bin/env python3
"""Copie le site de veille (docs/) vers le site netbudget.app, servi sur /ejp-tech-actu.

Usage :
  python3 scripts/publier_netbudget.py <dossier website/public du dépôt netbudget>

Le site netbudget (Vercel, cleanUrls, sans slash final) sert /ejp-tech-actu sans « / » :
les liens relatifs (veille.json, a-propos.html) pointeraient alors à la racine du domaine.
On ajoute donc <base href="/ejp-tech-actu/"> dans chaque page, plus un noindex pour ne pas
mélanger la veille avec le référencement de NetBudget.
"""

import re
import shutil
import sys
from pathlib import Path

CHEMIN = "/ejp-tech-actu/"
DOCS = Path(__file__).resolve().parent.parent / "docs"
AJOUT = f'<base href="{CHEMIN}">\n<meta name="robots" content="noindex">\n'


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cible = Path(sys.argv[1]) / CHEMIN.strip("/")
    cible.mkdir(parents=True, exist_ok=True)
    for page in ("index.html", "a-propos.html"):
        html = (DOCS / page).read_text(encoding="utf-8")
        if "<base " not in html:
            html = re.sub(r"(<meta charset=[^>]*>\n?)", lambda m: m.group(1) + AJOUT, html, count=1, flags=re.I)
        (cible / page).write_text(html, encoding="utf-8")
    shutil.copyfile(DOCS / "veille.json", cible / "veille.json")
    print(f"Publié dans {cible}")


if __name__ == "__main__":
    main()
