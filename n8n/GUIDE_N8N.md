# EJP Tech Décrypte avec n8n — guide de démarrage

Ce workflow prend **une actualité de la veille** choisie pour notre public (critères tirés du rapport du stand),
la fait passer par les **6 questions EJP Tech Décrypte** et rédige un **Reel Instagram** (3 hooks, script minuté, CTA,
couverture) et un **carrousel**, avec la légende et les hashtags. Moins de 450 mots au total.
Le résultat est une *proposition* : un humain valide toujours avant publication.

```
Lancer (manuel) ─────────────┐
Tous les 2 jours à 10h (auto) ┴→ 1. Choisir l'article → 2. Lire la veille → 3. Sélectionner l'article
       → 4. Lire la page de l'article → 5. Préparer la demande → 6. Claude → 7. Résultat → (8. ClickUp)
```

Exemple de résultat : [exemples/2026-10-08_meta-muse.md](exemples/2026-10-08_meta-muse.md)

---

## 1. Installer n8n (10 min, une seule fois)

Deux options :

- **n8n Cloud** (le plus simple pour travailler en équipe) : créer un compte sur n8n.io. Essai gratuit, puis abonnement.
- **Sur ton Mac, gratuit** (parfait pour tester) : Docker Desktop doit être lancé, puis dans un terminal :
  ```
  docker run -d --restart unless-stopped --name n8n -p 5678:5678 -e GENERIC_TIMEZONE=Europe/Paris -e TZ=Europe/Paris -v n8n_data:/home/node/.n8n n8nio/n8n
  ```
  Ouvre http://localhost:5678 et crée ton compte local. Tes workflows sont conservés entre deux lancements.
  n8n tourne en arrière-plan et redémarre avec Docker. Pour le lancement automatique, le Mac doit être allumé à 10 h
  (voir section 5).

## 2. Créer une clé API Claude (5 min, une seule fois)

1. Va sur https://platform.claude.com, connecte-toi, puis **API Keys > Create Key**. Copie la clé (elle commence par `sk-ant-`).
2. Ajoute un peu de crédit dans **Billing** : 5 $ suffisent pour 50 à 70 décryptages (0,07 à 0,10 $ chacun).
3. Ne colle jamais cette clé dans un fichier, un message ou ClickUp. Elle ne va que dans n8n (étape 3).

## 3. Importer le workflow (5 min, une seule fois)

1. Dans n8n : **Create workflow**, puis menu **⋯** en haut à droite > **Import from File…** > choisis `n8n/ejp_tech_decrypte.json`.
2. Double-clique sur le nœud **6. Claude - EJP Tech Decrypte**.
   - *Authentication* : **Generic Credential Type** ; *Generic Auth Type* : **Header Auth**.
   - *Credential for Header Auth* : **Create new credential**. La fenêtre a 3 zones :
     - **Le titre en haut** (cliquable) : le nom de la credential dans n8n, mets `Anthropic API`.
     - **Name** : le nom technique de l'en-tête HTTP. Écris exactement `x-api-key` : pas ton prénom, pas un libellé.
       C'est ce champ qui dit à Claude « voici la clé ». Avec un autre nom, l'erreur est
       « x-api-key header is required ».
     - **Value** : ta clé `sk-ant-…`.
     - **Save**.
3. **Save** le workflow (Cmd + S).

## 4. Utiliser le workflow (2 min par article)

1. Double-clique sur **1. Choisir l'article** et remplis :

   | Champ | À quoi ça sert | Exemple |
   |---|---|---|
   | `lien_article` | Le lien **d'un article** (celui sur lequel tu cliques dans la veille, pas l'adresse de la veille elle-même). **Vide, ou l'adresse de la veille = choix automatique** du meilleur article des derniers jours pour notre public | `https://next.ink/260011/…` |
   | `format` | `reel`, `carrousel` ou `les deux` | `les deux` |
   | `consigne` | Facultatif : un angle, une contrainte | `angle étudiants en partiel` |
   | `jours` | Période du choix automatique | `3` |
   | `veille_json_url` | Données de la veille, copie publique sur netbudget.app, à ne pas toucher | |

2. Clique sur **Execute workflow** (en bas). Compte environ 1 minute.
3. Clique sur le nœud **7. Resultat**. Champs utiles :
   - `decryptage` : le texte complet (lien, brief, Reel, carrousel, légende, à vérifier), c'est lui qui va dans ClickUp ;
   - `reel`, `carrousel`, `legende` : chaque partie séparément, si tu veux les mettre dans des champs ou sous-tâches ClickUp ;
   - `raison_choix` : pourquoi cet article (par exemple « frein n°1 : données personnelles (29 %) ») ;
   - `cout_estime` : 0,07 à 0,10 $ ;
   - `autres_candidats` : les 5 meilleurs articles du moment, si tu veux en traiter un autre.
4. Dans ClickUp, la section « À vérifier » sert de grille de validation avant tournage.

Astuce n8n : chaque nœud montre ce qu'il a reçu et produit (onglets *Input* et *Output*). C'est le meilleur moyen de comprendre ce qui se passe, ou de trouver ce qui bloque.

## 5. Lancement automatique (tous les 2 jours à 10 h)

Le workflow contient un second déclencheur, **Tous les 2 jours a 10h**. En automatique, `lien_article` est vide :
le workflow choisit le meilleur article pour notre public, en sautant ceux déjà décryptés.

1. Ouvre le workflow, puis active-le avec l'interrupteur **Active** (ou le bouton **Publish**, selon ta version) en haut à droite.
   Sans activation, rien ne part tout seul.
2. Pour changer de rythme, double-clique sur le déclencheur :
   - **Days Between Triggers** : `2` = tous les 2 jours, `1` = tous les jours ;
   - **Trigger at Hour** : `10am`.
   L'heure est celle de Paris (réglage du workflow).
3. **Condition** : n8n doit tourner à 10 h.
   - **n8n Cloud** : toujours allumé, rien à faire.
   - **Sur ton Mac** : le Mac doit être allumé (pas en veille), avec Docker Desktop lancé. Dans les réglages de Docker Desktop,
     coche *Start Docker Desktop when you sign in*. Si le Mac dort à 10 h, ce lancement est perdu (il n'est pas rattrapé).
4. Pour voir ce qui s'est passé : onglet **Executions** du workflow.

**Quel rythme choisir ?** Tous les 2 jours, c'est 3 à 4 propositions par semaine pour 1 à 1,50 $ par mois.
5 $ durent donc environ 4 mois. Tous les jours, c'est 2 à 3 $ par mois, soit environ 2 mois. L'objectif fixé dans les KPI étant de 1 à 2 décryptages
publiés par semaine, tous les 2 jours laisse déjà le choix sans saturer la liste ClickUp.

## 6. Si ça ne marche pas

| Message | Cause | Solution |
|---|---|---|
| « x-api-key header is required » | Le champ **Name** de la credential n'est pas `x-api-key` | Le corriger (étape 3.2) |
| « Aucun article : colle un lien… » | Les données de la veille sont illisibles | Ouvre `veille_json_url` dans un navigateur. En attendant, colle un lien dans `lien_article`, ça marche toujours |
| « Appel à Claude refusé : invalid x-api-key » | Clé mal copiée | Refaire l'étape 3.2 |
| « … credit balance is too low » | Plus de crédit | Recharger dans Billing |
| `texte_article` = « résumé seulement » | Le site bloque la lecture automatique | Le décryptage est fait sur le titre et le résumé, donc tous les faits sont à vérifier. Choisis plutôt une autre source sur le même sujet |
| « Réponse coupée » | Texte trop long | Relancer avec `format` = `reel` ou `carrousel` |
| Dans ClickUp, on voit des `##`, des `**` ou des `|` | Option *Markdown Content* non activée dans le nœud ClickUp | **Add Field > Markdown Content** : activé |
| Tâche ClickUp avec un titre mais sans description | Champ *Content* absent, ou pas en mode Expression | Dans le nœud ClickUp : **Add Field > Content**, bascule sur **Expression**, colle `{{ $json.decryptage }}` |

## 7. Envoyer le résultat dans ClickUp (15 min, une seule fois)

Le décryptage arrive directement comme une tâche ClickUp, assignée et notifiée sur le téléphone de l'équipe via l'app ClickUp.

**a. Clé ClickUp**
Dans ClickUp : ton avatar > **Settings** > **Apps** > **API Token** > *Generate*. Copie la clé, qui commence par `pk_`.
C'est une clé personnelle : les tâches seront créées en ton nom.

**b. Ajouter le nœud**
1. Survole le nœud **7. Resultat**, clique sur le **+** à sa droite, cherche **ClickUp**, puis choisis **Create a task**.
2. *Credential* > **Create new credential** > *ClickUp API* > colle la clé `pk_…` > **Save**.
3. Choisis dans les listes déroulantes **Team** (ton espace), **Space**, **Folder** (« ACTU TECH »), **List** (« VEILLE & SOURCING » ou ta liste de décryptages).
4. **Name** : clique sur le champ, passe en mode **Expression**, puis colle :
   `🔎 Décrypte : {{ $json.titre }}`
5. **Add Field** > **Content**, en mode Expression :
   `{{ $json.decryptage }}`
   Puis **Add Field** > **Markdown Content** et active-le. Sans cette option, ClickUp affiche les `##` et les `**` tels quels
   au lieu des titres et du gras.
6. Facultatif, toujours via **Add Field** :
   - **Status** : le statut de ta liste qui veut dire « à valider » (par exemple `TO REVIEW`, en respectant les majuscules) ;
   - **Assignees** : la personne qui valide ;
   - **Due Date**.
7. Renomme le nœud `8. ClickUp - creer la tache`, puis **Save** et **Execute workflow**.

Le lien de l'article (`{{ $json.lien_source }}`) se trouve déjà en tête du texte. Pour remplir aussi le champ personnalisé
« Source URL », il faut son identifiant : **Add Field** > **Custom Fields**. C'est à faire dans un second temps.

**Et WhatsApp ?** C'est possible, mais lourd : il faut un compte Meta Business, un numéro dédié vérifié, et des modèles de
messages validés par Meta. Le plus simple, dans l'ordre :
1. Les **notifications de l'app ClickUp** (déjà sur vos téléphones) : rien à ajouter, il suffit d'assigner la tâche.
2. **Telegram** : nœud *Telegram > Send Message*, avec un bot créé en 2 minutes via @BotFather, gratuit et sans validation.
   Message conseillé : titre + lien de la tâche ClickUp, pas le décryptage complet.
3. **WhatsApp** : nœud *WhatsApp Business Cloud*, seulement si l'équipe y tient vraiment.

## 8. La page de veille

La veille est publiée sur **https://www.netbudget.app/ejp-tech-actu**, mise à jour chaque jour par le robot
(si le secret `NETBUDGET_TOKEN` est configuré). Le workflow lit ses données (`veille.json`) à cette adresse,
car le dépôt GitHub est privé. L'ancienne adresse `eglisejp-tech.github.io/veille-actu-tech` reste en 404, c'est normal.

## 9. Modifier le comportement

- **Le ton, le canevas, les formats** : `src/prompt_systeme.md`. Il contient aussi les chiffres du rapport du stand
  (audience, outils, freins, formats préférés), que Claude prend en compte à chaque décryptage.
- **Le choix automatique** : `src/3_selectionner.js`. Les critères viennent du rapport du stand : outils utilisés
  (ChatGPT, Claude, Gemini, Canva…), freins (données personnelles 29 %, confiance 23 %), usages (études 61 %, rédaction,
  visuels), emploi et argent. Les sujets trop techniques ou business sont pénalisés.
- Après modification : `python3 n8n/src/build.py`, puis réimporter `ejp_tech_decrypte.json` dans n8n.
- **Réimporter sans perdre ton nœud ClickUp** : dans l'ancien workflow, clique sur le nœud ClickUp puis Cmd + C.
  Dans le nouveau, Cmd + V, puis relie « 7. Resultat » au nœud collé (glisser le petit rond de droite).
  Resélectionne la credential « Anthropic API » dans le nœud 6, active le nouveau workflow et désactive (ou supprime) l'ancien.
  On peut aussi modifier directement dans n8n, mais ces changements ne seront pas dans le dépôt.

Modèle utilisé : Claude Opus 5.5 (`claude-opus-5-5`). Un mécanisme de secours (« fallback ») est activé : si Claude refuse
un article, la demande est automatiquement relancée sur un autre modèle.

## Prochaines étapes possibles

1. Remplacer « Lancer » par un **formulaire n8n** (Form Trigger) : un lien à partager à l'équipe, sans ouvrir n8n.
2. Déclencher automatiquement le workflow quand une tâche ClickUp passe en « À décrypter » (nœud *ClickUp Trigger*).
