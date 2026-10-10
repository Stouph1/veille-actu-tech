#!/usr/bin/env python3
"""Assemble le workflow n8n (ejp_tech_decrypte.json) à partir des sources de ce dossier.

Modifier le prompt ou le code : éditer prompt_systeme.md ou les fichiers .js, puis
  python3 n8n/src/build.py
et réimporter le fichier ejp_tech_decrypte.json dans n8n.
"""

import json
from pathlib import Path

SRC = Path(__file__).parent
OUT = SRC.parent / "ejp_tech_decrypte.json"
# Copie publique publiée chaque jour sur netbudget.app (le dépôt GitHub est privé).
VEILLE_URL = "https://www.netbudget.app/ejp-tech-actu/veille.json"

prompt = (SRC / "prompt_systeme.md").read_text(encoding="utf-8").strip()
code = {name: (SRC / f"{name}.js").read_text(encoding="utf-8") for name in ("3_selectionner", "5_preparer", "7_resultat")}
code["5_preparer"] = code["5_preparer"].replace("__PROMPT_SYSTEME__", json.dumps(prompt, ensure_ascii=False))


def node(name, type_, version, x, params, **extra):
    return {"id": f"ejp-{x // 220}", "name": name, "type": type_, "typeVersion": version, "position": [x, 300], "parameters": params, **extra}


def champ(i, name, value, type_="string"):
    return {"id": f"champ-{i}", "name": name, "value": value, "type": type_}


nodes = [
    node("Lancer", "n8n-nodes-base.manualTrigger", 1, 0, {}),
    # Lancement automatique : actif seulement quand le workflow est activé dans n8n.
    # Tous les 2 jours à 10 h (heure de Paris) ; mettre daysInterval à 1 pour tous les jours.
    {**node("Tous les 2 jours a 10h", "n8n-nodes-base.scheduleTrigger", 1.2, 0, {
        "rule": {"interval": [{"field": "days", "daysInterval": 2, "triggerAtHour": 10, "triggerAtMinute": 0}]},
    }), "id": "ejp-auto", "position": [0, 520]},
    node("1. Choisir l article", "n8n-nodes-base.set", 3.4, 220, {
        "mode": "manual",
        "assignments": {"assignments": [
            champ(1, "lien_article", ""),
            champ(2, "format", "les deux"),
            champ(3, "consigne", ""),
            champ(4, "jours", 3, "number"),
            champ(5, "veille_json_url", VEILLE_URL),
        ]},
        "options": {},
    }),
    node("2. Lire la veille", "n8n-nodes-base.httpRequest", 4.2, 440, {
        "url": "={{ $json.veille_json_url }}",
        "options": {"response": {"response": {"neverError": True, "responseFormat": "json"}}, "timeout": 30000},
    }, onError="continueRegularOutput", alwaysOutputData=True),
    node("3. Selectionner l article", "n8n-nodes-base.code", 2, 660, {"jsCode": code["3_selectionner"]}),
    node("4. Lire la page de l article", "n8n-nodes-base.httpRequest", 4.2, 880, {
        "url": "={{ $json.article.lien }}",
        "sendHeaders": True,
        "headerParameters": {"parameters": [{"name": "User-Agent", "value": "Mozilla/5.0 (compatible; EJPTechDecrypte/1.0)"}]},
        "options": {"response": {"response": {"neverError": True, "responseFormat": "text", "outputPropertyName": "data"}}, "timeout": 30000},
    }, onError="continueRegularOutput", alwaysOutputData=True),
    node("5. Preparer la demande", "n8n-nodes-base.code", 2, 1100, {"jsCode": code["5_preparer"]}),
    node("6. Claude - EJP Tech Decrypte", "n8n-nodes-base.httpRequest", 4.2, 1320, {
        "method": "POST",
        "url": "https://api.anthropic.com/v1/messages",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "anthropic-version", "value": "2023-06-01"},
            {"name": "anthropic-beta", "value": "server-side-fallback-2026-07-01"},
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.requete) }}",
        "options": {"response": {"response": {"neverError": True, "responseFormat": "json"}}, "timeout": 300000},
    }),
    node("7. Resultat", "n8n-nodes-base.code", 2, 1540, {"jsCode": code["7_resultat"]}),
]

order = [n["name"] for n in nodes if n["id"] != "ejp-auto"]
connections = {a: {"main": [[{"node": b, "type": "main", "index": 0}]]} for a, b in zip(order, order[1:])}
connections["Tous les 2 jours a 10h"] = {"main": [[{"node": "1. Choisir l article", "type": "main", "index": 0}]]}

workflow = {
    "id": "ejpTechDecrypte1",
    "name": "EJP Tech Décrypte - article vers carrousel et script",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1", "timezone": "Europe/Paris"},
    "pinData": {},
}
OUT.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Écrit : {OUT}")
