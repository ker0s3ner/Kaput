"""Local LLM integration via Ollama for OSINT data consolidation."""
import re
import json
import requests

OLLAMA_BASE = "http://localhost:11434"
_PREFERRED = [
    "deepseek-r1:14b", "dolphin3:8b", "dolphin3", "llama3.2",
    "llama3.1", "llama3", "llama2", "deepseek-r1", "deepseek",
    "mistral", "gemma4:12b", "gemma4", "dolphin", "gemma2:latest",
    "gemma2", "gemma", "phi3", "phi", "qwen",
]


def list_models():
    """Return list of available Ollama model names, or [] if Ollama is not running."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return []


def best_model(models=None):
    """Pick the best available model from the list."""
    if models is None:
        models = list_models()
    if not models:
        return None
    lower = [m.lower() for m in models]
    for pref in _PREFERRED:
        for i, ml in enumerate(lower):
            if pref in ml:
                return models[i]
    return models[0]


def analyze_osint(osint_data: dict, model: str = None, stream_callback=None) -> str:
    """
    Send collected OSINT data to a local Ollama model for analysis.

    osint_data keys used:
      query, query_type, found (list of profile dicts),
      contacts (dict: emails, phones), cascade_usernames

    stream_callback: optional callable(text_chunk) for streaming output.
    Returns the full response text, or None on failure.
    """
    models = list_models()
    if not models:
        return None
    if model is None:
        model = best_model(models)

    prompt = _build_prompt(osint_data)
    use_stream = stream_callback is not None

    try:
        r = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={"model": model, "prompt": prompt, "stream": use_stream},
            timeout=180,
            stream=use_stream,
        )
        if r.status_code != 200:
            return None

        if use_stream:
            chunks = []
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    chunk = obj.get("response", "")
                    if chunk:
                        chunks.append(chunk)
                        stream_callback(chunk)
                    if obj.get("done"):
                        break
                except Exception:
                    pass
            return "".join(chunks)
        else:
            return r.json().get("response", "")

    except Exception as exc:
        return f"[LLM Error: {exc}]"


def _build_prompt(data: dict) -> str:
    lines = [
        "You are an OSINT analyst. Below is raw data collected about a person from public sources.",
        "Analyze ALL the data and write a consolidated profile report.",
        "Only report facts supported by the data. Mark uncertain items with [?].",
        "Be concise and structured. Do NOT invent information not present in the data.",
        "",
        "=== COLLECTED OSINT DATA ===",
        f"Initial query: {data.get('query', 'unknown')}  (type: {data.get('query_type', 'unknown')})",
        "",
    ]

    for entry in data.get("found", []):
        platform = entry.get("platform", "")
        username = entry.get("username", "")
        url = entry.get("url", "")
        detail = entry.get("detail") or {}
        lines.append(f"[{platform}]  username: {username}")
        lines.append(f"  URL: {url}")
        for k, v in detail.items():
            if v and k != "links_in_bio":
                lines.append(f"  {k}: {str(v)[:300]}")
        bio_links = detail.get("links_in_bio", "")
        if bio_links:
            lines.append(f"  linked accounts in bio: {bio_links}")
        lines.append("")

    contacts = data.get("contacts", {})
    emails = contacts.get("emails", [])
    phones = contacts.get("phones", [])
    if emails:
        lines.append(f"Extracted emails: {', '.join(emails)}")
    if phones:
        lines.append(f"Extracted phone numbers: {', '.join(phones)}")

    cascade = data.get("cascade_usernames", [])
    if cascade:
        lines.append(f"Additional usernames discovered via chain discovery: {', '.join(cascade)}")

    intel = data.get("intel", {})
    breach = intel.get("breach", {})
    if breach.get("breaches"):
        lines.append(f"Email breach databases: {', '.join(breach['breaches'][:20])}")
    rep = breach.get("emailrep", {})
    if rep.get("reputation"):
        lines.append(f"Email reputation: {rep['reputation']} | suspicious: {rep.get('suspicious',False)}")
    if rep.get("profiles"):
        lines.append(f"Email seen on profiles: {', '.join(rep['profiles'])}")
    paste_hits = intel.get("paste_hits", [])
    if paste_hits:
        lines.append(f"Found in {len(paste_hits)} paste/leak site(s): " +
                     " | ".join(h.get("url","") for h in paste_hits[:4]))

    lines += [
        "",
        "=== REPORT (write it now) ===",
        "Produce a clear dossier with these sections:",
        "1. IDENTITY   — real name (if found), age estimate, gender",
        "2. USERNAMES  — all confirmed handles per platform",
        "3. CONTACT    — emails, phone numbers",
        "4. LOCATION   — cities, countries, regions mentioned",
        "5. SOCIAL     — follower counts, activity level, notable stats",
        "6. PERSONAL   — interests, hobbies, lifestyle clues from bios",
        "7. CONNECTIONS — people mentioned (friends, family, partners)",
        "8. WORK / EDU  — workplace or school mentions",
        "9. LINKED ACCS — chain-discovered accounts from bios",
        "10. CONFIDENCE — reliability of this data and caveats",
        "",
    ]
    return "\n".join(lines)
