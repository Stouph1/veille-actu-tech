# Veille Actu Tech : mise en place (une seule fois, ~10 min)

## Structure du dépôt

```
veille-actu-tech/
├── veille_rss.py                  le script (30 sources, tri et scoring)
├── veille.json / veille.csv       la base complète (tous les articles collectés)
├── seen.json                      liens déjà vus (déduplication)
├── .github/workflows/veille.yml   exécution automatique quotidienne
└── docs/
    ├── index.html                 la page web (recherche, filtres thème / pertinence / langue / source)
    └── veille.json                les 60 derniers jours, écrits par le script pour le site
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

Chaque jour à 08h (Paris), GitHub lance le script. Il interroge les 30 sources
en parallèle (quelques secondes), ne garde que les articles des 7 derniers jours,
élimine les doublons (liens nettoyés de leurs paramètres de tracking, titres identiques
entre sources), écarte le bruit (articles sponsorisés, bons plans, promos), puis classe
chaque article :

- **Thème** : Cybersécurité, Régulation / éthique, Modèles & produits IA, Business / marché,
  Infrastructure, Société / usages, ou « Autre / à qualifier ». Les mots-clés sont comptés
  sur des mots entiers (« ia » ne matche plus dans « média »), en français et en anglais,
  et le thème qui cumule le plus de matches gagne.
- **Pertinence** : score = 2 points par mot-clé fort (IA, faille, RGPD, OpenAI…), 1 point par
  mot-clé moyen (cloud, startup, GPU…), bonus +1 pour les sources spécialisées.
  Haute ≥ 10, Moyenne ≥ 5, Basse sinon. Le score brut est conservé dans la colonne `score`.

Le site n'affiche que les 60 derniers jours pour rester rapide ; la base `veille.json` / `veille.csv`
garde tout l'historique. Personne n'a rien à faire. Ton PC peut être éteint.

## Sources suivies

| Famille | Sources |
|---|---|
| IA (fr) | ActuIA, Developpez.com |
| Tech généraliste (fr) | Numerama, ZDNet France, Le Monde Informatique, Le Monde Pixels, Siècle Digital, L'Usine Digitale, Next, Silicon.fr, LeMagIT, Clubic |
| Cyber et institutions (fr) | Numerama Cyberguerre, CERT-FR Alertes, CERT-FR Actualités, CNIL |
| Tech généraliste (en) | The Verge, Ars Technica, TechCrunch, The Register, Wired, MIT Technology Review |
| Cyber (en) | BleepingComputer, The Hacker News, Krebs on Security, Schneier on Security |
| Éditeurs et experts IA (en) | OpenAI News, Google AI Blog, Hugging Face Blog, Simon Willison |

Les flux RSS, Atom et RDF sont acceptés.

## Ajouter ou retirer une source

Dans `veille_rss.py`, liste `SOURCES` en haut du fichier, une ligne par source :
```python
{"name": "Numerama", "url": "https://www.numerama.com/feed/", "categorie": "Tech", "langue": "fr", "strict": True},
```
- `categorie` : `IA`, `Cyber`, `Institution` (bonus de pertinence +1) ou `Tech`.
- `langue` : `fr` ou `en`, utilisée par le filtre du site.
- `strict` : `True` pour un média généraliste, seuls les articles rattachés à un thème sont gardés ;
  `False` pour une source spécialisée dont on veut tout.

Commit + push, c'est tout. Pour ajuster les thèmes, les mots-clés ou les seuils, modifier `THEMES`,
`PERTINENCE_HAUTE`, `PERTINENCE_MOYENNE` et les seuils dans `score_text`.

## Tester en local

```bash
python3 veille_rss.py                 # collecte réelle, met à jour la base et docs/veille.json
python3 veille_rss.py fichier.xml     # parse un flux téléchargé, sans réseau
python3 -m http.server -d docs 8000   # puis ouvrir http://localhost:8000
```

## Plus tard, ClickUp

Le workflow pourra pousser chaque nouvel article vers l'API ClickUp
(ou via n8n) sans rien changer au reste. La base CSV/JSON reste la source.
