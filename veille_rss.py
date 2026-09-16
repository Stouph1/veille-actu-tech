#!/usr/bin/env python3

import csv
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

SOURCES = [
    {"name": "ActuIA", "url": "https://www.actuia.com/feed/", "categorie": "IA", "langue": "fr", "strict": False},
    {"name": "Developpez.com", "url": "https://www.developpez.com/index/rss", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Numerama", "url": "https://www.numerama.com/feed/", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Numerama Cyberguerre", "url": "https://www.numerama.com/cyberguerre/feed/", "categorie": "Cyber", "langue": "fr", "strict": True},
    {"name": "ZDNet France", "url": "https://www.zdnet.fr/feeds/rss/actualites/", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Le Monde Informatique", "url": "https://www.lemondeinformatique.fr/flux-rss/thematique/toutes-les-actualites/rss.xml", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Le Monde Pixels", "url": "https://www.lemonde.fr/pixels/rss_full.xml", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Siècle Digital", "url": "https://siecledigital.fr/feed/", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "L'Usine Digitale", "url": "https://www.usine-digitale.fr/rss", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Next", "url": "https://next.ink/feed/", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Silicon.fr", "url": "https://www.silicon.fr/feed", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "LeMagIT", "url": "https://www.lemagit.fr/rss/ContentSyndication.xml", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "Clubic", "url": "https://www.clubic.com/feed/news.rss", "categorie": "Tech", "langue": "fr", "strict": True},
    {"name": "CERT-FR Alertes", "url": "https://www.cert.ssi.gouv.fr/alerte/feed/", "categorie": "Cyber", "langue": "fr", "strict": False},
    {"name": "CERT-FR Actualités", "url": "https://www.cert.ssi.gouv.fr/actualite/feed/", "categorie": "Cyber", "langue": "fr", "strict": False},
    {"name": "CNIL", "url": "https://www.cnil.fr/fr/rss.xml", "categorie": "Institution", "langue": "fr", "strict": False},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "categorie": "Tech", "langue": "en", "strict": True},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "categorie": "Tech", "langue": "en", "strict": True},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "categorie": "Tech", "langue": "en", "strict": True},
    {"name": "The Register", "url": "https://www.theregister.com/headlines.atom", "categorie": "Tech", "langue": "en", "strict": True},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss", "categorie": "Tech", "langue": "en", "strict": True},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "categorie": "Tech", "langue": "en", "strict": True},
    {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "categorie": "Cyber", "langue": "en", "strict": False},
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "categorie": "Cyber", "langue": "en", "strict": False},
    {"name": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/", "categorie": "Cyber", "langue": "en", "strict": False},
    {"name": "Schneier on Security", "url": "https://www.schneier.com/feed/atom/", "categorie": "Cyber", "langue": "en", "strict": True},
    {"name": "OpenAI News", "url": "https://openai.com/news/rss.xml", "categorie": "IA", "langue": "en", "strict": False},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "categorie": "IA", "langue": "en", "strict": False},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "categorie": "IA", "langue": "en", "strict": True},
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/", "categorie": "IA", "langue": "en", "strict": True},
]

THEMES = {
    "Cybersécurité": [
        "faille", "failles", "vulnérabilité", "vulnérabilités", "vulnerability", "vulnerabilities", "cve", "kev", "zero-day",
        "ransomware", "rançongiciel", "cyberattaque", "cyberattaques", "cyberattack", "cybersécurité", "cybersecurity",
        "piratage", "pirates", "hacker", "hackers", "malware", "phishing", "hameçonnage", "fuite de données", "data breach",
        "breach", "exploit", "exploited", "botnet", "cert-fr", "anssi", "cisa", "patch", "correctif", "backdoor", "spyware",
    ],
    "Régulation / éthique": [
        "ai act", "rgpd", "gdpr", "régulation", "regulation", "réglementation", "cnil", "loi", "law", "décret", "éthique",
        "ethics", "gouvernance", "commission européenne", "european commission", "parlement", "sénat", "tribunal", "procès",
        "lawsuit", "amende", "fine", "antitrust", "dma", "dsa", "souveraineté", "sovereignty", "vie privée", "privacy",
        "surveillance", "droits d'auteur", "copyright", "arcom", "autorité",
    ],
    "Modèles & produits IA": [
        "gpt", "chatgpt", "claude", "anthropic", "openai", "mistral", "gemini", "llama", "deepseek", "copilot", "grok",
        "llm", "modèle", "modèles", "model", "models", "agent", "agents", "agentique", "agentic", "ia générative",
        "generative ai", "intelligence artificielle", "artificial intelligence", "machine learning", "apprentissage automatique",
        "hugging face", "open source", "open-source", "benchmark", "raisonnement", "reasoning", "multimodal", "mcp",
    ],
    "Business / marché": [
        "lève", "levée", "levée de fonds", "funding", "raises", "rachat", "acquisition", "acquiert", "acquires", "valorisation",
        "valuation", "investissement", "investment", "milliard", "milliards", "billion", "millions", "ipo", "bourse",
        "chiffre d'affaires", "revenue", "licenciements", "layoffs", "startup", "start-up", "partenariat", "partnership",
    ],
    "Infrastructure": [
        "datacenter", "datacenters", "data center", "centre de données", "gpu", "gpus", "puce", "puces", "chip", "chips",
        "semi-conducteur", "semiconductor", "nvidia", "amd", "tsmc", "cloud", "supercalculateur", "supercomputer",
        "nucléaire", "nuclear", "énergie", "energy", "électricité", "electricity", "réseau", "fibre", "5g", "6g", "quantique", "quantum",
    ],
    "Société / usages": [
        "éducation", "education", "école", "school", "étudiants", "students", "emploi", "employment", "travail", "jobs",
        "enfants", "children", "kids", "jeunes", "adolescents", "teens", "santé", "health", "hôpital", "deepfake", "deepfakes",
        "désinformation", "disinformation", "misinformation", "réseaux sociaux", "social media", "tiktok", "instagram",
        "addiction", "bien-être", "mental health", "démocratie", "élections", "elections", "religion", "église",
    ],
}

PERTINENCE_HAUTE = [
    "ia", "ai", "intelligence artificielle", "artificial intelligence", "ia générative", "generative ai", "llm", "chatgpt",
    "openai", "anthropic", "claude", "mistral", "gemini", "google", "microsoft", "meta", "apple", "nvidia",
    "faille", "failles", "vulnérabilité", "vulnérabilités", "vulnerability", "vulnerabilities", "cve", "cisa", "exploited", "flaw", "flaws",
    "cyberattaque", "cyberattack", "ransomware", "rançongiciel", "zero-day", "fuite de données", "malware", "phishing",
    "data breach", "ai act", "rgpd", "cnil", "deepfake", "désinformation", "souveraineté", "commission européenne",
]
PERTINENCE_MOYENNE = [
    "cloud", "startup", "start-up", "levée", "funding", "régulation", "regulation", "agent", "agents", "modèle", "model",
    "open source", "gpu", "datacenter", "data center", "quantique", "quantum", "réseaux sociaux", "social media", "robot", "robots",
]

CATEGORIE_BONUS = {"IA": 1, "Cyber": 1, "Institution": 1, "Tech": 0}
MAX_AGE_DAYS = 7
MAX_ITEMS_PER_SOURCE = 25
SITE_RETENTION_DAYS = 60
RESUME_MAX = 280
STATUT_INITIAL = "À lire"
NOISE_RE = re.compile(r"\[sponso\]|sponsoris|\bbon plan\b|\bbons plans\b|\bpromo\b|\bpromotion\b|\bsoldes\b|french days|black friday|prime day|\bdeal\b|\bdeals\b|\bcode promo\b|^quoting\b|friday squid|\btest\b.*\bavis\b|\bà quel prix\b|meilleur prix|prix fou", re.IGNORECASE)
TRACKING_PARAMS = ("utm_", "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "xtor", "at_medium", "at_campaign")

OUT_DIR = Path(__file__).parent
CSV_PATH = OUT_DIR / "veille.csv"
JSON_PATH = OUT_DIR / "veille.json"
SEEN_PATH = OUT_DIR / "seen.json"
SITE_JSON_PATH = OUT_DIR / "docs" / "veille.json"

FIELDS = ["titre", "lien", "source", "categorie", "langue", "date", "theme", "resume", "pertinence", "score", "statut"]

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
ENTITIES = {"&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&#8217;": "'", "&#8230;": "…", "&hellip;": "…", "&rsquo;": "'", "&laquo;": "«", "&raquo;": "»"}


def compile_keywords(words: list[str]) -> re.Pattern:
    alts = sorted((re.escape(w.lower()) for w in words), key=len, reverse=True)
    return re.compile(r"(?<![\w-])(?:" + "|".join(alts) + r")(?![\w-])", re.IGNORECASE)


THEME_PATTERNS = {theme: compile_keywords(kws) for theme, kws in THEMES.items()}
HAUTE_PATTERN = compile_keywords(PERTINENCE_HAUTE)
MOYENNE_PATTERN = compile_keywords(PERTINENCE_MOYENNE)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; VeilleActuTech/1.0; +https://stouph1.github.io/veille-actu-tech/)", "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def clean(text: str) -> str:
    text = TAG_RE.sub(" ", text or "")
    for k, v in ENTITIES.items():
        text = text.replace(k, v)
    return SPACE_RE.sub(" ", text).strip()


def strip_title(resume: str, titre: str) -> str:
    if titre and resume.lower().startswith(titre.lower()):
        resume = resume[len(titre):].lstrip(" .:-–—|")
    return resume


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.") + "…"


def normalize_link(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.lower().startswith(TRACKING_PARAMS)]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower() or "https", parts.netloc.lower(), path, urlencode(query), ""))


def strip_namespaces(root: ET.Element) -> None:
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]


def parse_date(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except Exception:
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def first_text(el: ET.Element, *names: str) -> str:
    for name in names:
        found = el.find(name)
        if found is not None and (found.text or "").strip():
            return found.text
    return ""


def entry_link(el: ET.Element) -> str:
    for link in el.findall("link"):
        rel = link.get("rel", "alternate")
        href = link.get("href") or (link.text or "")
        if rel == "alternate" and href.strip():
            return href.strip()
    return (first_text(el, "link", "guid", "id") or "").strip()


def score_text(text: str, categorie: str) -> tuple[str, int, str]:
    theme_scores = {theme: len(pat.findall(text)) for theme, pat in THEME_PATTERNS.items()}
    best_theme, best_score = max(theme_scores.items(), key=lambda kv: kv[1])
    theme = best_theme if best_score > 0 else "Autre / à qualifier"
    score = len(HAUTE_PATTERN.findall(text)) * 2 + len(MOYENNE_PATTERN.findall(text)) + CATEGORIE_BONUS.get(categorie, 0)
    if score >= 10:
        pertinence = "Haute"
    elif score >= 5:
        pertinence = "Moyenne"
    else:
        pertinence = "Basse"
    return theme, score, pertinence


def parse_feed(xml_bytes: bytes, source: dict, cutoff: datetime | None) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    strip_namespaces(root)
    entries = list(root.iter("item")) + list(root.iter("entry"))
    records = []
    for el in entries[:MAX_ITEMS_PER_SOURCE]:
        titre = clean(first_text(el, "title"))
        lien = normalize_link(entry_link(el))
        if not titre or not lien or NOISE_RE.search(titre):
            continue
        dt = parse_date(first_text(el, "pubDate", "published", "updated", "date"))
        if cutoff and dt and dt < cutoff:
            continue
        resume = truncate(strip_title(clean(first_text(el, "description", "summary", "content", "encoded")), titre), RESUME_MAX)
        blob = f"{titre} {titre} {resume}"
        theme, score, pertinence = score_text(blob, source["categorie"])
        if source.get("strict") and (theme == "Autre / à qualifier" or pertinence == "Basse"):
            continue
        records.append({
            "titre": titre,
            "lien": lien,
            "source": source["name"],
            "categorie": source["categorie"],
            "langue": source["langue"],
            "date": (dt or datetime.now(timezone.utc)).strftime("%Y-%m-%d"),
            "theme": theme,
            "resume": resume,
            "pertinence": pertinence,
            "score": score,
            "statut": STATUT_INITIAL,
        })
    return records


def collect(source: dict, cutoff: datetime | None) -> tuple[dict, list[dict], str]:
    try:
        return source, parse_feed(fetch(source["url"]), source, cutoff), ""
    except Exception as e:
        return source, [], f"{type(e).__name__}: {e}"


def load_seen() -> set:
    if SEEN_PATH.exists():
        return set(json.loads(SEEN_PATH.read_text()))
    return set()


def title_key(titre: str) -> str:
    return re.sub(r"[^\w]+", " ", titre.lower()).strip()


def dedupe(records: list[dict], seen: set) -> list[dict]:
    kept, titles = [], set()
    for r in sorted(records, key=lambda r: (r["date"], r["score"]), reverse=True):
        tk = title_key(r["titre"])
        if r["lien"] in seen or tk in titles:
            continue
        titles.add(tk)
        kept.append(r)
    return kept


SOURCE_BY_NAME = {s["name"]: s for s in SOURCES}


def upgrade(r: dict) -> dict:
    r = {f: r.get(f, "") for f in FIELDS}
    r["source"] = r["source"].replace(" (test local)", "")
    src = SOURCE_BY_NAME.get(r["source"], {"categorie": "Tech", "langue": "fr"})
    r["categorie"] = r["categorie"] or src["categorie"]
    r["langue"] = r["langue"] or src["langue"]
    if not isinstance(r["score"], int):
        r["theme"], r["score"], r["pertinence"] = score_text(f"{r['titre']} {r['titre']} {r['resume']}", r["categorie"])
    r["resume"] = strip_title(r["resume"], r["titre"])
    r["statut"] = r["statut"] or STATUT_INITIAL
    return r


def save_central(new_records: list[dict]) -> list[dict]:
    existing = json.loads(JSON_PATH.read_text()) if JSON_PATH.exists() else []
    by_link = {}
    for r in existing + new_records:
        r = upgrade(r)
        by_link[r["lien"]] = r
    merged = sorted(by_link.values(), key=lambda r: (r["date"], r.get("score") or 0), reverse=True)
    JSON_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2))
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(merged)
    return merged


def save_site(merged: list[dict]) -> None:
    limit = (datetime.now(timezone.utc) - timedelta(days=SITE_RETENTION_DAYS)).strftime("%Y-%m-%d")
    site = [r for r in merged if r["date"] >= limit]
    SITE_JSON_PATH.parent.mkdir(exist_ok=True)
    SITE_JSON_PATH.write_text(json.dumps({"maj": datetime.now(timezone.utc).isoformat(timespec="minutes"), "articles": site}, ensure_ascii=False))


def main():
    seen = load_seen()
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    collected = []

    if len(sys.argv) > 1:
        src = {"name": "Test local", "categorie": "Tech", "langue": "fr", "strict": False}
        collected = parse_feed(Path(sys.argv[1]).read_bytes(), src, None)
    else:
        with ThreadPoolExecutor(max_workers=8) as ex:
            for source, records, error in ex.map(lambda s: collect(s, cutoff), SOURCES):
                if error:
                    print(f"[ERREUR] {source['name']} : {error}")
                else:
                    print(f"[OK] {source['name']:24} {len(records):3} article(s) récent(s)")
                collected += records

    new_records = dedupe(collected, seen)
    merged = save_central(new_records)
    save_site(merged)

    if not new_records:
        print("Aucun nouvel article.")
        return

    seen.update(r["lien"] for r in new_records)
    SEEN_PATH.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2))

    print(f"\n{len(new_records)} nouvel(s) article(s) ajouté(s) :")
    for r in new_records:
        print(f"  [{r['pertinence']:^7}] {r['theme']:22} | {r['source']:20} | {r['titre'][:60]}")


if __name__ == "__main__":
    main()
