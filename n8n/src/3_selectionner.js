// Choisit l'article à décrypter.
// - Lien d'article collé dans « 1. Choisir l'article » : on le cherche dans la veille.
// - Vide (ou adresse de la veille) : choix automatique selon les attentes du public (rapport du stand).
const choix = $('1. Choisir l article').first().json;
const veille = $input.first().json || {};
const articles = Array.isArray(veille.articles) ? veille.articles : [];

// Articles déjà décryptés par les lancements automatiques (mémoire du workflow, voir « 7. Resultat »).
const memoire = $getWorkflowStaticData('global');
const dejaFaits = new Set(memoire.deja_decryptes || []);

const normaliser = (u) => (u || '').trim().replace(/[?#].*$/, '').replace(/\/+$/, '').toLowerCase();
const lienBrut = normaliser(choix.lien_article);
const lien = /ejp-tech-actu$|veille-actu-tech$/.test(lienBrut) ? '' : lienBrut;

// Pondération tirée du rapport du stand (102 réponses, septembre 2026).
// Plus un sujet touche une part importante du public, plus il pèse.
const SIGNAUX = [
  { nom: 'outil utilisé par le public', points: 4, mots: ['chatgpt', 'openai', 'claude', 'gemini', 'canva', 'copilot', 'meta ai', 'instagram', 'tiktok', 'snapchat', 'whatsapp'] },
  { nom: 'frein n°1 : données personnelles (29 %)', points: 5, mots: ['données personnelles', 'vie privée', 'confidentialité', 'fuite de données', 'exposés', 'mémoire', 'mot de passe', 'privacy', 'personal data', 'tracking', 'surveillance'] },
  { nom: 'frein n°2 : confiance dans les réponses (23 %)', points: 4, mots: ['hallucination', 'erreur', 'se trompe', 'fiable', 'fiabilité', 'désinformation', 'deepfake', 'fake', 'vérifier', 'restituent mal'] },
  { nom: 'usage : études et révisions (61 %)', points: 4, mots: ['étudiant', 'étudiants', 'école', 'université', 'examen', 'partiel', 'bac', 'révision', 'apprendre', 'cours', 'élève'] },
  { nom: 'usage : rédiger, résumer, s\'organiser', points: 3, mots: ['rédiger', 'rédaction', 'résumer', 'résumé', 'organiser', 'agenda', 'traduire', 'traduction', 'productivité'] },
  { nom: 'usage : créer des visuels (60 %)', points: 3, mots: ['image', 'images', 'visuel', 'vidéo générée', 'sora', 'midjourney', 'dessin'] },
  { nom: 'jeunes actifs : emploi, CV, argent', points: 3, mots: ['emploi', ' cv', 'recrutement', 'stage', 'alternance', 'job', 'salaire', 'arnaque', 'escroquerie', 'payant', 'gratuit', 'prix', 'abonnement'] },
];
const BONUS_THEME = { 'Société / usages': 3, 'Régulation / éthique': 2, 'Modèles & produits IA': 1, 'Cybersécurité': 1 };
// Trop technique ou trop « business » pour ce public.
const MALUS = ['levée de fonds', ' lève ', 'valorisation', 'milliards de dollars', 'datacenter', 'centre de données', ' gpu', 'nvidia', ' api', ' sdk', 'kubernetes', 'serveur', 'b2b', 'cve-', 'zero-day', 'exploit'];

function evaluer(a) {
  const texte = ` ${a.titre} ${a.titre} ${a.resume} `.toLowerCase();
  let score = BONUS_THEME[a.theme] || 0;
  const raisons = [];
  for (const s of SIGNAUX) {
    if (s.mots.some((m) => texte.includes(m))) { score += s.points; raisons.push(s.nom); }
  }
  score -= 3 * MALUS.filter((m) => texte.includes(m)).length;
  if (a.langue === 'fr') score += 2; // exemples et contexte plus proches du public
  if (a.pertinence === 'Basse') score -= 4;
  return { score, raisons };
}

let article = null;
let mode = '';
let raisons = [];

if (lien) {
  article = articles.find((a) => normaliser(a.lien) === lien) || null;
  mode = article ? 'lien collé, trouvé dans la veille' : 'lien collé, absent de la veille (on lira la page directement)';
  if (!article) {
    article = { titre: '', lien: choix.lien_article.trim(), source: (choix.lien_article.match(/\/\/([^/]+)/) || [, ''])[1].replace(/^www\./, ''), date: '', theme: '', resume: '' };
  }
}

const jours = Number(choix.jours) || 3;
const depuis = new Date(Date.now() - jours * 86400000).toISOString().slice(0, 10);
const candidats = articles
  .filter((a) => a.date >= depuis && !dejaFaits.has(normaliser(a.lien)))
  .map((a) => ({ ...a, ...evaluer(a) }))
  .sort((x, y) => y.score - x.score)
  .slice(0, 5);

if (!article) {
  if (!candidats.length) {
    throw new Error("Aucun article : colle un lien dans « 1. Choisir l'article », ou vérifie que l'URL de la veille est lisible (voir le guide).");
  }
  article = candidats[0];
  raisons = article.raisons;
  mode = `choix automatique (meilleur score public EJP sur ${jours} jours)`;
}

return [{
  json: {
    article,
    mode_selection: mode,
    raison_choix: raisons.join(' · '),
    autres_candidats: candidats.map((c) => `${c.score} pts | ${c.date} | ${c.source} | ${c.titre} | ${c.lien}`),
    format: choix.format,
    consigne: choix.consigne || '',
  },
}];
