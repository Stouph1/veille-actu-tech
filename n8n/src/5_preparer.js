// Extrait le texte lisible de la page de l'article et prépare la demande envoyée à Claude.
const sel = $('3. Selectionner l article').first().json;
const page = $input.first().json || {};
const html = typeof page.data === 'string' ? page.data : '';

function texteLisible(h) {
  let t = h
    .replace(/<(script|style|noscript|svg|nav|header|footer|aside|form)[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<\/(p|h[1-6]|li|div|br)>/gi, '\n')
    .replace(/<[^>]+>/g, ' ');
  t = t
    .replace(/&nbsp;|&#160;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#039;|&#39;|&rsquo;|&#8217;/g, "'")
    .replace(/&laquo;/g, '«').replace(/&raquo;/g, '»').replace(/&eacute;/g, 'é').replace(/&egrave;/g, 'è').replace(/&agrave;/g, 'à')
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)));
  // On garde les lignes qui ressemblent à des phrases (évite menus et boutons).
  return t.split('\n').map((l) => l.replace(/\s+/g, ' ').trim()).filter((l) => l.length > 60).join('\n');
}

let texte = texteLisible(html);
const LIMITE = 12000; // environ 2 000 mots : l'essentiel d'un article, pour un coût maîtrisé
const tronque = texte.length > LIMITE;
if (tronque) texte = texte.slice(0, LIMITE);
const complet = texte.length > 800;

const a = sel.article;
const formats = {
  'carrousel': 'carrousel seulement (pas de section Reel)',
  'reel': 'reel seulement (pas de section Carrousel)',
  'video': 'reel seulement (pas de section Carrousel)',
  'les deux': 'Reel ET carrousel',
};

const demande = [
  `Article à décrypter :`,
  `- Titre : ${a.titre || 'non fourni (déduis-le du texte)'}`,
  `- Source : ${a.source || 'non précisée'}`,
  `- Date : ${a.date || 'non précisée'}`,
  `- Lien : ${a.lien}`,
  `- Thème (classement automatique de la veille) : ${a.theme || 'non classé'}`,
  `- Résumé RSS : ${a.resume || 'aucun'}`,
  ``,
  complet
    ? `Texte de l'article${tronque ? ' (tronqué)' : ''} :\n"""\n${texte}\n"""`
    : `Texte complet indisponible (page illisible ou protégée). Travaille à partir du titre et du résumé RSS, et applique la règle « résumé seulement ».`,
  ``,
  `Format demandé : ${formats[sel.format] || formats['les deux']}`,
  sel.consigne ? `Consigne de l'équipe : ${sel.consigne}` : '',
].filter((l) => l !== '').join('\n');

return [{
  json: {
    texte_complet: complet,
    requete: {
      model: 'claude-opus-5-5',
      max_tokens: 8000,
      output_config: { effort: 'medium' },
      fallbacks: 'default',
      system: __PROMPT_SYSTEME__,
      messages: [{ role: 'user', content: demande }],
    },
  },
}];
