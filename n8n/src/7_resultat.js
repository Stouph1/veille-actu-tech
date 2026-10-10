// Met en forme la réponse de Claude : le texte final, plus de quoi contrôler (coût, article, alternatives).
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

const u = r.usage || {};
// Tarifs Claude Opus 5.5 : 4 $ / million de jetons en entrée, 20 $ / million en sortie.
const cout = ((u.input_tokens || 0) * 4 + (u.output_tokens || 0) * 20) / 1e6;

const titre = ((texte.match(/^#\s+(.+)$/m) || [])[1] || sel.article.titre || 'Décryptage').trim();

return [{
  json: {
    titre,
    lien_source: sel.article.lien,
    decryptage: texte + (r.stop_reason === 'max_tokens' ? '\n\n⚠️ Réponse coupée (trop longue) : relance avec un seul format.' : ''),
    article: `${sel.article.titre} — ${sel.article.lien}`,
    selection: sel.mode_selection,
    texte_article: prep.texte_complet ? 'complet' : 'résumé seulement : faits à vérifier',
    cout_estime: `${cout.toFixed(3)} $`,
    autres_candidats: sel.autres_candidats,
    statut: 'Proposition : à valider avant publication',
  },
}];
