# EJP Tech Décrypte avec n8n — guide de démarrage

Ce workflow prend **une actualité de la veille**, la fait passer par les **6 questions EJP Tech Décrypte**
et rédige un **carrousel** et/ou un **script vidéo courte**. Le résultat est une *proposition* :
un humain valide toujours avant publication.

```
Lancer → 1. Choisir l'article → 2. Lire la veille → 3. Sélectionner l'article
       → 4. Lire la page de l'article → 5. Préparer la demande → 6. Claude → 7. Résultat
```

Exemple de résultat : [exemples/2026-10-08_meta-muse.md](exemples/2026-10-08_meta-muse.md)

---

## 1. Installer n8n (10 min, une seule fois)

Deux options :

- **n8n Cloud** (le plus simple pour travailler en équipe) : créer un compte sur n8n.io. Essai gratuit, puis abonnement.
- **Sur ton Mac, gratuit** (parfait pour tester) : Docker Desktop doit être lancé, puis dans un terminal :
  ```
  docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
  ```
  Ouvre http://localhost:5678 et crée ton compte local. Tes workflows sont conservés entre deux lancements.

## 2. Créer une clé API Claude (5 min, une seule fois)

1. Va sur https://platform.claude.com, connecte-toi, puis **API Keys > Create Key**. Copie la clé (elle commence par `sk-ant-`).
2. Ajoute un peu de crédit dans **Billing** : 5 $ suffisent pour environ 50 décryptages.
3. Ne colle jamais cette clé dans un fichier, un message ou ClickUp. Elle ne va que dans n8n (étape 3).

## 3. Importer le workflow (5 min, une seule fois)

1. Dans n8n : **Create workflow**, puis menu **⋯** en haut à droite > **Import from File…** > choisis `n8n/ejp_tech_decrypte.json`.
2. Double-clique sur le nœud **6. Claude - EJP Tech Decrypte**.
   - *Authentication* : **Generic Credential Type** ; *Generic Auth Type* : **Header Auth**.
   - *Credential for Header Auth* : **Create new credential**.
     - **Name** : `x-api-key`
     - **Value** : ta clé `sk-ant-…`
     - Renomme la credential `Anthropic API` (en haut de la fenêtre), puis **Save**.
3. **Save** le workflow (Cmd + S).

## 4. Utiliser le workflow (2 min par article)

1. Double-clique sur **1. Choisir l'article** et remplis :

   | Champ | À quoi ça sert | Exemple |
   |---|---|---|
   | `lien_article` | Le lien de l'actu choisie (site de veille, ClickUp ou n'importe quel média). **Vide = choix automatique** du meilleur article des derniers jours pour notre public | `https://next.ink/260011/…` |
   | `format` | `carrousel`, `video` ou `les deux` | `les deux` |
   | `consigne` | Facultatif : un angle, une contrainte | `angle étudiants en partiel` |
   | `jours` | Période du choix automatique | `3` |
   | `veille_json_url` | Adresse des données de la veille, à ne pas toucher | |

2. Clique sur **Execute workflow** (en bas). Compte environ 1 minute.
3. Clique sur le nœud **7. Resultat** : le champ `decryptage` contient le texte complet, à copier dans ClickUp.
   Les autres champs t'aident à contrôler le résultat :
   - `selection` : comment l'article a été choisi ;
   - `texte_article` : indique si Claude a lu l'article complet ou seulement le résumé ;
   - `cout_estime` : environ 0,10 $ ;
   - `autres_candidats` : les 5 meilleurs articles du moment, si tu veux en traiter un autre.
4. Dans ClickUp, la tâche passe en **Proposition**, puis la section « À vérifier avant publication » sert de grille de validation.

Astuce n8n : chaque nœud montre ce qu'il a reçu et produit (onglets *Input* et *Output*). C'est le meilleur moyen de comprendre ce qui se passe, ou de trouver ce qui bloque.

## 5. Si ça ne marche pas

| Message | Cause | Solution |
|---|---|---|
| « Aucun article : colle un lien… » | Les données de la veille sont illisibles (dépôt GitHub privé) | Colle un lien dans `lien_article` : ça marche toujours. Pour le choix automatique, voir la section 6 |
| « Appel à Claude refusé : invalid x-api-key » | Clé mal copiée | Refaire l'étape 3.2 |
| « … credit balance is too low » | Plus de crédit | Recharger dans Billing |
| `texte_article` = « résumé seulement » | Le site bloque la lecture automatique | Le décryptage est fait sur le titre et le résumé, donc tous les faits sont à vérifier. Choisis plutôt une autre source sur le même sujet |
| « Réponse coupée » | Texte trop long | Relancer avec `format` = `carrousel` ou `video` |

## 6. Et la page de veille en 404 ?

Le workflow n'en a pas besoin : il lit directement le fichier `docs/veille.json` du dépôt.
Mais si le dépôt est **privé**, n8n ne peut pas lire ce fichier (seul le mode « lien collé » marche), et GitHub Pages
ne publie pas non plus le site sur un compte gratuit, d'où le 404. Deux solutions :

- **Rendre le dépôt public** (recommandé) : *Settings > General > Danger Zone > Change visibility*. La veille ne contient que des
  titres, liens et résumés publics, sans aucune donnée personnelle. Ensuite *Settings > Pages* : Branch `main`, dossier `/docs`.
- **Le garder privé** : passer l'organisation GitHub en offre payante pour Pages, et créer un jeton GitHub pour n8n.

Si le dépôt a changé d'adresse, mets à jour `veille_json_url` dans le nœud 1
(format : `https://raw.githubusercontent.com/<compte>/veille-actu-tech/main/docs/veille.json`).

## 7. Modifier le comportement

- **Le ton, le canevas, les formats** : `src/prompt_systeme.md`. Il contient aussi les chiffres du rapport du stand
  (audience, outils, freins, formats préférés), que Claude prend en compte à chaque décryptage.
- **Le choix automatique** : `src/3_selectionner.js` (mots qui parlent à notre public, bonus par thème).
- Après modification : `python3 n8n/src/build.py`, puis réimporter `ejp_tech_decrypte.json` dans n8n.
  On peut aussi modifier directement dans n8n, mais ces changements ne seront pas dans le dépôt.

Modèle utilisé : Claude Opus 5.5 (`claude-opus-5-5`). Un mécanisme de secours (« fallback ») est activé : si Claude refuse
un article, la demande est automatiquement relancée sur un autre modèle.

## Prochaines étapes possibles

1. Remplacer « Lancer » par un **formulaire n8n** (Form Trigger) : un lien à partager à l'équipe, sans ouvrir n8n.
2. Envoyer le résultat directement dans **ClickUp** (nœud ClickUp, avec un jeton API ClickUp) : création d'une tâche « Proposition ».
3. Déclencher automatiquement le workflow quand une tâche ClickUp passe en « À décrypter ».
