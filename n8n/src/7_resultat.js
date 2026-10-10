// Met en forme la réponse de Claude : un texte prêt pour ClickUp, plus chaque partie séparée.
const r = $input.first().json || {};
const sel = $('3. Selectionner l article').first().json;
const prep = $('5. Preparer la demande').first().json;

if (r.error) {
  const msg = typeof r.error === 'string' ? r.error : (r.error.message || JSON.stringify(r.error));
  throw new Error(`Appel à Claude refusé : ${msg}. Vérifie la clé API (credential « Anthropic API ») et le crédit du compte.`);
}
if (r.stop_reason === 'refusal') {
  throw new Error("Claude a refusé de traiter cet article. Choisis-en un autre ou reformule la consigne.");
}

const texte = (r.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('\n').trim();
if (!texte) throw new Error('Réponse vide de Claude. Relance le workflow.');

// Découpe par sections « ## Titre ».
const sections = {};
for (const bloc of texte.split(/^## /m).slice(1)) {
  const [entete, ...corps] = bloc.split('\n');
  sections[entete.trim().toLowerCase()] = corps.join('\n').trim();
}
const titre = ((texte.match(/^#\s+(.+)$/m) || [])[1] || sel.article.titre || 'Décryptage').trim();

// Mémorise l'article pour que les lancements automatiques ne le reprennent pas.
const memoire = $getWorkflowStaticData('global');
const lienNorm = (sel.article.lien || '').trim().replace(/[?#].*$/, '').replace(/\/+$/, '').toLowerCase();
memoire.deja_decryptes = [...new Set([...(memoire.deja_decryptes || []), lienNorm])].slice(-200);

const u = r.usage || {};
// Tarifs Claude Opus 5.5 : 4 $ / million de jetons en entrée, 20 $ / million en sortie.
const cout = ((u.input_tokens || 0) * 4 + (u.output_tokens || 0) * 20) / 1e6;

const coupe = r.stop_reason === 'max_tokens' ? '\n\n⚠️ Réponse coupée : relance avec un seul format.' : '';
const avertissement = prep.texte_complet ? '' : '⚠️ Article non lisible en entier : rédigé à partir du résumé, tous les faits sont à vérifier.\n\n';

return [{
  json: {
    titre,
    lien_source: sel.article.lien,
    // Texte prêt pour la description de la tâche ClickUp (même nom de champ qu'avant).
    decryptage: `${avertissement}🔗 ${sel.article.lien}\n\n${texte.replace(/^#\s+.+\n+/, '')}${coupe}`,
    brief: sections['brief'] || '',
    reel: sections['reel'] || '',
    carrousel: sections['carrousel'] || '',
    legende: sections['légende'] || sections['legende'] || '',
    a_verifier: sections['à vérifier'] || '',
    selection: sel.mode_selection,
    raison_choix: sel.raison_choix,
    cout_estime: `${cout.toFixed(3)} $`,
    autres_candidats: sel.autres_candidats,
  },
}];
