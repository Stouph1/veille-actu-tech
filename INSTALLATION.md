# Veille Actu Tech : mise en place (une seule fois, ~10 min)

## Structure du dépôt

```
veille-actu-tech/
├── veille_rss.py                  le script (déjà testé)
├── .github/workflows/veille.yml   exécution automatique quotidienne
└── docs/
    ├── index.html                 la page web
    └── veille.json                les données affichées (mises à jour par le bot)
```

## Étapes

1. **Créer le dépôt GitHub**
   Sur github.com : New repository, nom `veille-actu-tech`, public (obligatoire pour GitHub Pages gratuit).

2. **Pousser les fichiers**
   ```bash
   git clone https://github.com/TON_COMPTE/veille-actu-tech.git
   # copier les fichiers du zip dans le dossier en respectant la structure
   cd veille-actu-tech
   git add .
   git commit -m "Pipeline de veille v0"
   git push
   ```

3. **Autoriser le bot à écrire**
   Sur GitHub : Settings > Actions > General > Workflow permissions > cocher "Read and write permissions" > Save.

4. **Activer le site**
   Settings > Pages > Source : "Deploy from a branch" > Branch : `main`, dossier `/docs` > Save.
   Le site sera à l'adresse : `https://TON_COMPTE.github.io/veille-actu-tech/`

5. **Tester sans attendre demain**
   Onglet Actions > "Veille quotidienne" > Run workflow.
   Une minute plus tard : nouveaux articles commités et site à jour.

## Fonctionnement quotidien

Chaque jour à 08h (Paris), GitHub lance le script, récupère les nouveaux
articles ActuIA, les ajoute à la base et met à jour la page web.
Personne n'a rien à faire. Ton PC peut être éteint.

## Ajouter une source

Dans `veille_rss.py`, section SOURCES en haut du fichier :
```python
SOURCES = [
    {"name": "ActuIA", "url": "https://www.actuia.com/feed/"},
    {"name": "Numerama", "url": "https://www.numerama.com/feed/"},
]
```
Commit + push, c'est tout.

## Plus tard, ClickUp

Le workflow pourra pousser chaque nouvel article vers l'API ClickUp
(ou via n8n) sans rien changer au reste. La base CSV/JSON reste la source.
