// Choisit l'article à décrypter.
// - Si un lien a été collé dans « 1. Choisir l'article » : on le cherche dans la veille.
// - Sinon : on propose automatiquement le meilleur candidat pour l'audience EJP Tech.
const choix = $('1. Choisir l article').first().json;
const veille = $input.first().json || {};
const articles = Array.isArray(veille.articles) ? veille.articles : [];

const normaliser = (u) => (u || '').trim().replace(/[?#].*$/, '').replace(/\/+$/, '').toLowerCase();
// Le lien du site de veille lui-même (ou rien) = choix automatique.
const lienBrut = normaliser(choix.lien_article);
const lien = /ejp-tech-actu$|veille-actu-tech$/.test(lienBrut) ? '' : lienBrut;

// Ce qui parle à l'audience du stand (étudiants, ChatGPT au quotidien, données perso, confiance).
const MOTS_AUDIENCE = [
  'chatgpt', 'claude', 'gemini', 'canva', 'copilot', 'meta', 'tiktok', 'instagram', 'snapchat', 'whatsapp',
  'données personnelles', 'vie privée', 'confidentialité', 'mémoire', 'privacy', 'personal data',
  'étudiant', 'école', 'université', 'examen', 'révision', 'jeunes', 'adolescent', 'emploi', 'cv', 'recrutement',
  'arnaque', 'scam', 'hallucination', 'désinformation', 'deepfake', 'gratuit', 'smartphone', 'mot de passe',
];
const BONUS_THEME = { 'Société / usages': 4, 'Régulation / éthique': 3, 'Modèles & produits IA': 2, 'Cybersécurité': 1 };

function scoreEjp(a) {
  const texte = `${a.titre} ${a.resume}`.toLowerCase();
  let s = BONUS_THEME[a.theme] || 0;
  for (const m of MOTS_AUDIENCE) if (texte.includes(m)) s += 2;
  if (a.pertinence === 'Haute') s += 2;
  if (a.pertinence === 'Basse') s -= 4;
  if (a.langue === 'fr') s += 2;
  return s;
}

let article = null;
let mode = '';

if (lien) {
  article = articles.find((a) => normaliser(a.lien) === lien) || null;
  mode = article ? 'lien collé, trouvé dans la veille' : 'lien collé, absent de la veille (on lira la page directement)';
  if (!article) {
    article = { titre: '', lien: choix.lien_article.trim(), source: (choix.lien_article.match(/\/\/([^/]+)/) || [, ''])[1].replace(/^www\./, ''), date: '', theme: '', resume: '' };
  }
}

const depuis = new Date(Date.now() - (Number(choix.jours) || 3) * 86400000).toISOString().slice(0, 10);
const candidats = articles
  .filter((a) => a.date >= depuis)
  .map((a) => ({ ...a, score_ejp: scoreEjp(a) }))
  .sort((x, y) => y.score_ejp - x.score_ejp)
  .slice(0, 5);

if (!article) {
  if (!candidats.length) {
    throw new Error("Aucun article : colle un lien dans « 1. Choisir l'article », ou vérifie que l'URL de la veille est lisible (voir le guide).");
  }
  article = candidats[0];
  mode = `choix automatique (meilleur score EJP sur ${Number(choix.jours) || 3} jours)`;
}

return [{
  json: {
    article,
    mode_selection: mode,
    autres_candidats: candidats.map((c) => `${c.score_ejp} pts | ${c.date} | ${c.source} | ${c.titre} | ${c.lien}`),
    format: choix.format,
    consigne: choix.consigne || '',
  },
}];
