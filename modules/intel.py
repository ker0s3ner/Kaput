"""
Specialized intelligence modules — all free, no API keys required.

  breach_check(email)      — XposedOrNot + EmailRep.io breach lookups
  gravatar_lookup(email)   — email hash → Gravatar username / avatar
  crt_sh_lookup(domain)    — certificate transparency subdomain enumeration
  paste_search(query)      — DDG paste-site search for leaked data
  phone_enrich(phone)      — ITU prefix → country + carrier hint
"""

import re
import json
import hashlib
import time
import requests
from urllib.parse import quote_plus

_HDR = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json, text/html,*/*;q=0.8",
}
_DDG = "https://html.duckduckgo.com/html/?q={}&kl=us-en"

# ── Breach check ────────────────────────────────────────────────────────────

def breach_check(email: str, timeout: int = 8) -> dict:
    """
    Check an email against free breach APIs.
    Returns {
        "breaches":  [str, ...],   # breach names
        "pastes":    int,          # number of paste leaks (if known)
        "emailrep":  dict,         # raw EmailRep summary
        "sources":   [str, ...],   # which APIs responded
    }
    """
    result = {"breaches": [], "pastes": 0, "emailrep": {}, "sources": []}

    # 1 ── XposedOrNot (no key required, GDPR-compliant)
    try:
        r = requests.get(
            f"https://api.xposedornot.com/v1/check-email/{quote_plus(email)}",
            headers=_HDR, timeout=timeout
        )
        if r.status_code == 200:
            d = r.json()
            # response is {"Error": "Not found"} or {"exposures": {"breaches": [...]}}
            exposures = d.get("exposures") or d.get("breaches") or {}
            if isinstance(exposures, dict):
                for breach in exposures.get("breaches", []):
                    if isinstance(breach, dict):
                        result["breaches"].append(breach.get("name", str(breach)))
                    else:
                        result["breaches"].append(str(breach))
            elif isinstance(exposures, list):
                result["breaches"].extend(str(b) for b in exposures)
            result["sources"].append("XposedOrNot")
        elif r.status_code == 404:
            result["sources"].append("XposedOrNot")  # clean
    except Exception:
        pass

    # 2 ── EmailRep.io (free tier, no key, 100 req/day)
    try:
        r = requests.get(
            f"https://emailrep.io/{quote_plus(email)}",
            headers={**_HDR, "Accept": "application/json"},
            timeout=timeout,
        )
        if r.status_code == 200:
            d = r.json()
            result["emailrep"] = {
                "reputation":      d.get("reputation", ""),
                "suspicious":      d.get("suspicious", False),
                "references":      d.get("references", 0),
                "seen_in_breach":  d.get("details", {}).get("data_breach", False),
                "malicious_activity": d.get("details", {}).get("malicious_activity", False),
                "profiles":        d.get("details", {}).get("profiles", []),
                "first_seen":      d.get("details", {}).get("first_seen", ""),
                "last_seen":       d.get("details", {}).get("last_seen", ""),
            }
            # EmailRep sometimes lists breach names
            for b in d.get("details", {}).get("breach_details", {}).get("breaches", []):
                if b and b not in result["breaches"]:
                    result["breaches"].append(b)
            result["sources"].append("EmailRep")
    except Exception:
        pass

    return result


# ── Gravatar ─────────────────────────────────────────────────────────────────

def gravatar_lookup(email: str, timeout: int = 6) -> dict:
    """
    Hash email → query Gravatar. Returns {"username", "display_name", "about",
    "avatar_url", "verified_accounts": [...]}.
    """
    result = {}
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    try:
        r = requests.get(
            f"https://www.gravatar.com/{h}.json",
            headers=_HDR, timeout=timeout
        )
        if r.status_code == 200:
            entry = r.json().get("entry", [{}])[0]
            result["username"]      = entry.get("preferredUsername", "")
            result["display_name"]  = entry.get("displayName", "")
            result["about"]         = (entry.get("aboutMe") or "")[:200]
            result["avatar_url"]    = f"https://www.gravatar.com/avatar/{h}"
            urls = []
            for u in entry.get("urls", []):
                if isinstance(u, dict) and u.get("value"):
                    urls.append(u["value"])
            accounts = []
            for acc in entry.get("accounts", []):
                if isinstance(acc, dict):
                    accounts.append(
                        f"{acc.get('shortname','')}: {acc.get('username','')}"
                    )
            if urls:      result["links"]             = " | ".join(urls[:6])
            if accounts:  result["verified_accounts"] = " | ".join(accounts[:6])
    except Exception:
        pass
    return {k: v for k, v in result.items() if v}


# ── Certificate transparency ─────────────────────────────────────────────────

def crt_sh_lookup(domain: str, timeout: int = 12) -> list:
    """
    Query crt.sh for all subdomains seen in public TLS certificates.
    Returns sorted list of unique subdomain strings.
    """
    subdomains = set()
    try:
        r = requests.get(
            f"https://crt.sh/?q=%.{domain}&output=json",
            headers=_HDR, timeout=timeout
        )
        if r.status_code == 200:
            for entry in r.json():
                name = entry.get("name_value", "")
                for sub in name.split("\n"):
                    sub = sub.strip().lower()
                    if sub.endswith(f".{domain}") or sub == domain:
                        sub = re.sub(r"^\*\.", "", sub)
                        if sub:
                            subdomains.add(sub)
    except Exception:
        pass
    return sorted(subdomains)


# ── Paste search ──────────────────────────────────────────────────────────────

_PASTE_SITES = [
    "pastebin.com", "paste.ee", "ghostbin.com", "privatebin.net",
    "hastebin.com", "gist.github.com", "pastes.io", "justpaste.it",
    "paste.mozilla.org", "ideone.com",
]

def paste_search(query: str, timeout: int = 10) -> list:
    """
    Search DuckDuckGo for the query across paste sites.
    Returns list of {"url", "title", "snippet"} dicts.
    """
    results = []
    sites   = " OR ".join(f"site:{s}" for s in _PASTE_SITES)
    q       = quote_plus(f'"{query}" ({sites})')
    try:
        from bs4 import BeautifulSoup
        r = requests.get(_DDG.format(q), headers=_HDR, timeout=timeout)
        soup = BeautifulSoup(r.text, "html.parser")
        for res in soup.select(".result")[:12]:
            title_el   = res.select_one(".result__title")
            snippet_el = res.select_one(".result__snippet")
            url_el     = res.select_one(".result__url")
            title   = title_el.get_text(strip=True)   if title_el   else ""
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            url     = url_el.get_text(strip=True)     if url_el     else ""
            if url and any(s in url for s in _PASTE_SITES):
                results.append({"url": url, "title": title, "snippet": snippet[:120]})
    except Exception:
        pass
    return results


# ── Phone enrichment ──────────────────────────────────────────────────────────

# ITU calling code → (country_name, region)
_PHONE_PREFIXES = {
    "1":   ("United States / Canada", "NANP"),
    "7":   ("Russia / Kazakhstan", "RU/KZ"),
    "20":  ("Egypt",        "AF"),
    "27":  ("South Africa", "AF"),
    "30":  ("Greece",       "EU"),
    "31":  ("Netherlands",  "EU"),
    "32":  ("Belgium",      "EU"),
    "33":  ("France",       "EU"),
    "34":  ("Spain",        "EU"),
    "36":  ("Hungary",      "EU"),
    "39":  ("Italy",        "EU"),
    "40":  ("Romania",      "EU"),
    "41":  ("Switzerland",  "EU"),
    "43":  ("Austria",      "EU"),
    "44":  ("United Kingdom", "EU"),
    "45":  ("Denmark",      "EU"),
    "46":  ("Sweden",       "EU"),
    "47":  ("Norway",       "EU"),
    "48":  ("Poland",       "EU"),
    "49":  ("Germany",      "EU"),
    "51":  ("Peru",         "SA"),
    "52":  ("Mexico",       "NA"),
    "53":  ("Cuba",         "NA"),
    "54":  ("Argentina",    "SA"),
    "55":  ("Brazil",       "SA"),
    "56":  ("Chile",        "SA"),
    "57":  ("Colombia",     "SA"),
    "58":  ("Venezuela",    "SA"),
    "60":  ("Malaysia",     "AS"),
    "61":  ("Australia",    "OC"),
    "62":  ("Indonesia",    "AS"),
    "63":  ("Philippines",  "AS"),
    "64":  ("New Zealand",  "OC"),
    "65":  ("Singapore",    "AS"),
    "66":  ("Thailand",     "AS"),
    "81":  ("Japan",        "AS"),
    "82":  ("South Korea",  "AS"),
    "84":  ("Vietnam",      "AS"),
    "86":  ("China",        "AS"),
    "90":  ("Turkey",       "EU/AS"),
    "91":  ("India",        "AS"),
    "92":  ("Pakistan",     "AS"),
    "93":  ("Afghanistan",  "AS"),
    "94":  ("Sri Lanka",    "AS"),
    "95":  ("Myanmar",      "AS"),
    "98":  ("Iran",         "AS"),
    "212": ("Morocco",      "AF"),
    "213": ("Algeria",      "AF"),
    "216": ("Tunisia",      "AF"),
    "218": ("Libya",        "AF"),
    "220": ("Gambia",       "AF"),
    "221": ("Senegal",      "AF"),
    "234": ("Nigeria",      "AF"),
    "254": ("Kenya",        "AF"),
    "255": ("Tanzania",     "AF"),
    "256": ("Uganda",       "AF"),
    "260": ("Zambia",       "AF"),
    "263": ("Zimbabwe",     "AF"),
    "351": ("Portugal",     "EU"),
    "352": ("Luxembourg",   "EU"),
    "353": ("Ireland",      "EU"),
    "354": ("Iceland",      "EU"),
    "355": ("Albania",      "EU"),
    "356": ("Malta",        "EU"),
    "357": ("Cyprus",       "EU"),
    "358": ("Finland",      "EU"),
    "359": ("Bulgaria",     "EU"),
    "370": ("Lithuania",    "EU"),
    "371": ("Latvia",       "EU"),
    "372": ("Estonia",      "EU"),
    "373": ("Moldova",      "EU"),
    "374": ("Armenia",      "AS"),
    "375": ("Belarus",      "EU"),
    "376": ("Andorra",      "EU"),
    "377": ("Monaco",       "EU"),
    "380": ("Ukraine",      "EU"),
    "381": ("Serbia",       "EU"),
    "382": ("Montenegro",   "EU"),
    "385": ("Croatia",      "EU"),
    "386": ("Slovenia",     "EU"),
    "387": ("Bosnia-Herzegovina", "EU"),
    "389": ("North Macedonia", "EU"),
    "420": ("Czech Republic", "EU"),
    "421": ("Slovakia",     "EU"),
    "370": ("Lithuania",    "EU"),
    "370": ("Lithuania",    "EU"),
    "502": ("Guatemala",    "NA"),
    "503": ("El Salvador",  "NA"),
    "504": ("Honduras",     "NA"),
    "505": ("Nicaragua",    "NA"),
    "506": ("Costa Rica",   "NA"),
    "507": ("Panama",       "NA"),
    "509": ("Haiti",        "NA"),
    "590": ("Guadeloupe",   "NA"),
    "591": ("Bolivia",      "SA"),
    "593": ("Ecuador",      "SA"),
    "595": ("Paraguay",     "SA"),
    "597": ("Suriname",     "SA"),
    "598": ("Uruguay",      "SA"),
    "670": ("East Timor",   "AS"),
    "673": ("Brunei",       "AS"),
    "674": ("Nauru",        "OC"),
    "675": ("Papua New Guinea", "OC"),
    "676": ("Tonga",        "OC"),
    "677": ("Solomon Islands", "OC"),
    "678": ("Vanuatu",      "OC"),
    "679": ("Fiji",         "OC"),
    "680": ("Palau",        "OC"),
    "850": ("North Korea",  "AS"),
    "852": ("Hong Kong",    "AS"),
    "853": ("Macau",        "AS"),
    "855": ("Cambodia",     "AS"),
    "856": ("Laos",         "AS"),
    "880": ("Bangladesh",   "AS"),
    "886": ("Taiwan",       "AS"),
    "960": ("Maldives",     "AS"),
    "961": ("Lebanon",      "AS"),
    "962": ("Jordan",       "AS"),
    "963": ("Syria",        "AS"),
    "964": ("Iraq",         "AS"),
    "965": ("Kuwait",       "AS"),
    "966": ("Saudi Arabia", "AS"),
    "967": ("Yemen",        "AS"),
    "968": ("Oman",         "AS"),
    "970": ("Palestine",    "AS"),
    "971": ("UAE",          "AS"),
    "972": ("Israel",       "AS"),
    "973": ("Bahrain",      "AS"),
    "974": ("Qatar",        "AS"),
    "975": ("Bhutan",       "AS"),
    "976": ("Mongolia",     "AS"),
    "977": ("Nepal",        "AS"),
    "992": ("Tajikistan",   "AS"),
    "993": ("Turkmenistan", "AS"),
    "994": ("Azerbaijan",   "AS"),
    "995": ("Georgia",      "AS"),
    "996": ("Kyrgyzstan",   "AS"),
    "998": ("Uzbekistan",   "AS"),
}


def phone_enrich(phone: str, timeout: int = 8) -> dict:
    """
    Enrich a phone number:
    - Strip to digits, match ITU prefix → country
    - DDG search for number on social/paste/public sites
    Returns {"country", "region", "formatted", "ddg_hits": [...]}
    """
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0") and not digits.startswith("00"):
        digits = digits[1:]  # local format — can't resolve without country context

    country = region = ""
    for length in (3, 2, 1):
        prefix = digits[:length]
        if prefix in _PHONE_PREFIXES:
            country, region = _PHONE_PREFIXES[prefix]
            break

    fmt = f"+{digits}" if digits else phone

    # DDG search for the number
    hits = []
    try:
        from bs4 import BeautifulSoup
        q = quote_plus(f'"{fmt}" OR "{phone}"')
        r = requests.get(_DDG.format(q), headers=_HDR, timeout=timeout)
        soup = BeautifulSoup(r.text, "html.parser")
        for el in soup.select(".result__title a")[:6]:
            text = el.get_text(strip=True)
            href = el.get("href", "")
            if text:
                hits.append({"title": text, "url": href})
    except Exception:
        pass

    return {k: v for k, v in {
        "country":   country,
        "region":    region,
        "formatted": fmt,
        "ddg_hits":  hits,
    }.items() if v}
