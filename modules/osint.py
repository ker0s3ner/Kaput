"""OSINT (Open Source Intelligence) gathering tools"""

import requests
import re
import json
import time
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from colorama import Fore, Style
from .utils import ColorPrinter


PLATFORMS = {
    "GitHub":         ("https://github.com/{}",                       "status"),
    "GitLab":         ("https://gitlab.com/{}",                       "status"),
    "Twitter":        ("https://twitter.com/{}",                      "content:@{}"),
    "Instagram":      ("https://www.instagram.com/{}/",               "content:\"username\":\"{}\""),
    "TikTok":         ("https://www.tiktok.com/@{}",                  "content:\"uniqueId\":\"{}\""),
    "Reddit":         ("https://www.reddit.com/user/{}/about.json",   "content:\"name\":\"{}\""),
    "YouTube":        ("https://www.youtube.com/@{}",                 "status"),
    "Twitch":         ("https://www.twitch.tv/{}",                    "content:\"login\":\"{}\""),
    "Steam":          ("https://steamcommunity.com/id/{}",            "content:steamID"),
    "Pinterest":      ("https://www.pinterest.com/{}/",               "status"),
    "Tumblr":         ("https://{}.tumblr.com",                       "status"),
    "SoundCloud":     ("https://soundcloud.com/{}",                   "status"),
    "Spotify":        ("https://open.spotify.com/user/{}",            "status"),
    "Flickr":         ("https://www.flickr.com/people/{}",            "status"),
    "Vimeo":          ("https://vimeo.com/{}",                        "status"),
    "DeviantArt":     ("https://www.deviantart.com/{}",               "status"),
    "Medium":         ("https://medium.com/@{}",                      "status"),
    "Quora":          ("https://www.quora.com/profile/{}",            "status"),
    "Keybase":        ("https://keybase.io/{}",                       "content:{}"),
    "HackerNews":     ("https://hacker-news.firebaseio.com/v0/user/{}.json", "content:\"id\":\"{}\""),
    "npm":            ("https://www.npmjs.com/~{}",                   "status"),
    "PyPI":           ("https://pypi.org/user/{}/",                   "status"),
    "DockerHub":      ("https://hub.docker.com/u/{}",                 "status"),
    "Patreon":        ("https://www.patreon.com/{}",                  "content:\"vanity\":\"{}\""),
    "Replit":         ("https://replit.com/@{}",                      "status"),
    "Codepen":        ("https://codepen.io/{}",                       "status"),
    "Behance":        ("https://www.behance.net/{}",                  "status"),
    "Dribbble":       ("https://dribbble.com/{}",                     "status"),
    "Fiverr":         ("https://www.fiverr.com/{}",                   "status"),
    "Telegram":       ("https://t.me/{}",                             "content:tgme_page_title"),
    "Snapchat":       ("https://www.snapchat.com/add/{}",             "content:snapchat.com/add/{}"),
    "Chess.com":      ("https://api.chess.com/pub/player/{}",         "content:\"username\":"),
    "Duolingo":       ("https://www.duolingo.com/2017-06-30/users?username={}", "content:\"username\":"),
    "Lichess":        ("https://lichess.org/api/user/{}",             "content:\"id\":\"{}\""),
    "Xbox":           ("https://xboxgamertag.com/search/{}",          "status"),
    "PSN":            ("https://psnprofiles.com/{}",                  "status"),
    "Roblox":         ("https://www.roblox.com/user.aspx?username={}", "status"),
    "Minecraft":      ("https://api.mojang.com/users/profiles/minecraft/{}", "content:\"name\":"),
    "Gravatar":       ("https://www.gravatar.com/{}",                 "status"),
    "About.me":       ("https://about.me/{}",                         "status"),
    "Linktree":       ("https://linktr.ee/{}",                        "status"),
    "Cashapp":        ("https://cash.app/${}",                        "content:cashtag"),
    "Venmo":          ("https://account.venmo.com/u/{}",              "status"),
    "GitLab Pages":   ("https://{}.gitlab.io",                        "status"),
    "HackerOne":      ("https://hackerone.com/{}",                    "status"),
    "Bugcrowd":       ("https://bugcrowd.com/{}",                     "status"),
    "Wattpad":        ("https://www.wattpad.com/user/{}",             "status"),
    "Imgur":          ("https://imgur.com/user/{}",                   "status"),
    "9GAG":           ("https://9gag.com/u/{}",                       "status"),
    "Letterboxd":     ("https://letterboxd.com/{}",                   "status"),
    "Goodreads":      ("https://www.goodreads.com/{}",                "status"),
    "Mix":            ("https://mix.com/{}",                          "status"),
    "Slashdot":       ("https://slashdot.org/~{}",                    "status"),
    "SourceForge":    ("https://sourceforge.net/u/{}/profile/",       "status"),
    "Trello":         ("https://trello.com/{}",                       "status"),
    "Codecademy":     ("https://www.codecademy.com/profiles/{}",      "status"),
    "Freecodecamp":   ("https://www.freecodecamp.org/{}",             "status"),
}

# Per-platform URL patterns used by SmartPersonLookup's web hunter
_PLATFORM_WEB_PATTERNS = {
    "Twitter":    (r'twitter\.com/([A-Za-z0-9_]{1,15})(?:/|\?|$)',      "twitter.com"),
    "Instagram":  (r'instagram\.com/([A-Za-z0-9_.]{1,30})(?:/|\?|$)',   "instagram.com"),
    "TikTok":     (r'tiktok\.com/@([A-Za-z0-9_.]{1,24})(?:/|\?|$)',     "tiktok.com"),
    "YouTube":    (r'youtube\.com/@([A-Za-z0-9_.]{1,30})(?:/|\?|$)',    "youtube.com"),
    "Reddit":     (r'reddit\.com/u(?:ser)?/([A-Za-z0-9_\-]{3,20})(?:/|\?|$)', "reddit.com"),
    "GitHub":     (r'github\.com/([A-Za-z0-9\-]{1,39})(?:/|\?|$)',      "github.com"),
    "LinkedIn":   (r'linkedin\.com/in/([A-Za-z0-9\-]{3,100})(?:/|\?|$)', "linkedin.com"),
    "Twitch":     (r'twitch\.tv/([A-Za-z0-9_]{4,25})(?:/|\?|$)',        "twitch.tv"),
    "Steam":      (r'steamcommunity\.com/id/([A-Za-z0-9_\-]{2,32})(?:/|\?|$)', "steamcommunity.com"),
    "Pinterest":  (r'pinterest\.com/([A-Za-z0-9_\-]{3,30})(?:/|\?|$)', "pinterest.com"),
    "SoundCloud": (r'soundcloud\.com/([A-Za-z0-9\-_]{3,40})(?:/|\?|$)', "soundcloud.com"),
}

_DDG_SEARCH_URL = "https://html.duckduckgo.com/html/?q={}&kl=us-en"
_SESSION_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def _check_platform(platform, url_template, check_rule, username, timeout=8,
                    display_url=None):
    """
    Check if username exists on a single platform.
    Returns (platform, display_url, found, detail).

    check_rule variants:
      "status"              — 200 = found
      "content:<needle>"    — 200 + needle in body
      "not_content:<needle>"— 200 + needle NOT in body  (Sherlock "message" type)
      "url_not:<bad_url>"   — 200 + final URL doesn't contain bad_url
    """
    probe_url = url_template.format(username)
    show_url  = display_url.format(username) if display_url else probe_url
    try:
        r = requests.get(probe_url, headers=_SESSION_HEADERS, timeout=timeout,
                         allow_redirects=True)
        if check_rule == "status":
            found = r.status_code == 200
        elif check_rule.startswith("content:"):
            needle = check_rule[8:].replace("{}", username)
            found  = r.status_code == 200 and needle.lower() in r.text.lower()
        elif check_rule.startswith("not_content:"):
            needle = check_rule[12:].lower()
            found  = r.status_code == 200 and (not needle or needle not in r.text.lower())
        elif check_rule.startswith("url_not:"):
            bad = check_rule[8:].lower()
            found = r.status_code == 200 and (not bad or bad not in r.url.lower())
        else:
            found = r.status_code == 200

        detail = _extract_profile_detail(platform, r.text, username) if found else None
        return (platform, show_url, found, detail)
    except Exception:
        return (platform, show_url, None, None)


def _extract_profile_detail(platform, html, username):
    """Deep per-platform profile scraper. Returns dict of found fields."""
    detail = {}
    try:
        # ── JSON-API platforms ──────────────────────────────────────────────
        if platform == "Reddit":
            d = json.loads(html).get("data", {})
            if d.get("created_utc"):
                detail["joined"]   = time.strftime("%Y-%m-%d", time.gmtime(d["created_utc"]))
            if d.get("total_karma") is not None:
                detail["karma"]    = f"{d['total_karma']:,}"
            if d.get("link_karma") is not None:
                detail["post_karma"] = f"{d['link_karma']:,}"
            if d.get("comment_karma") is not None:
                detail["comment_karma"] = f"{d['comment_karma']:,}"
            if d.get("subreddit", {}).get("public_description"):
                detail["bio"]      = d["subreddit"]["public_description"][:200]
            if d.get("icon_img"):
                detail["avatar"]   = d["icon_img"].split("?")[0]
            return {k: v for k, v in detail.items() if v}

        if platform == "HackerNews":
            d = json.loads(html) or {}
            if d.get("karma"):  detail["karma"]   = f"{d['karma']:,}"
            if d.get("created"): detail["joined"]  = str(d["created"])
            if d.get("about"):  detail["bio"]     = d["about"][:200]
            return {k: v for k, v in detail.items() if v}

        if platform == "Chess.com":
            d = json.loads(html)
            detail["name"]     = d.get("name", "")
            detail["title"]    = d.get("title", "")
            detail["country"]  = (d.get("country") or "").split("/")[-1]
            detail["joined"]   = time.strftime("%Y-%m-%d", time.gmtime(d["joined"])) if d.get("joined") else ""
            detail["last_on"]  = time.strftime("%Y-%m-%d", time.gmtime(d["last_online"])) if d.get("last_online") else ""
            detail["followers"] = str(d.get("followers", ""))
            if d.get("url"): detail["url"] = d["url"]
            return {k: v for k, v in detail.items() if v}

        if platform == "Lichess":
            d = json.loads(html)
            detail["name"]     = d.get("username", "")
            perf = d.get("perfs", {})
            ratings = [f"{k}:{v['rating']}" for k, v in perf.items() if isinstance(v, dict) and "rating" in v]
            if ratings: detail["ratings"] = "  ".join(ratings[:4])
            if d.get("createdAt"):
                detail["joined"]  = time.strftime("%Y-%m-%d", time.gmtime(d["createdAt"] / 1000))
            p = d.get("profile", {})
            if p.get("bio"):      detail["bio"]      = p["bio"][:200]
            if p.get("country"):  detail["country"]  = p["country"]
            if p.get("location"): detail["location"] = p["location"]
            if p.get("links"):    detail["links"]    = p["links"][:200]
            return {k: v for k, v in detail.items() if v}

        if platform == "Duolingo":
            users = json.loads(html).get("users", [])
            d = users[0] if users else {}
            detail["name"]      = d.get("name", "")
            detail["xp"]        = str(d.get("totalXp", ""))
            detail["streak"]    = f"{d.get('streak', 0)} days"
            detail["joined"]    = d.get("creationDate", "")
            detail["courses"]   = str(len(d.get("courses", [])))
            return {k: v for k, v in detail.items() if v}

        if platform == "Minecraft":
            d = json.loads(html)
            detail["name"] = d.get("name", "")
            detail["id"]   = d.get("id", "")
            return {k: v for k, v in detail.items() if v}

        # ── HTML platforms ──────────────────────────────────────────────────
        soup = BeautifulSoup(html, 'html.parser')

        # ── GitHub ──────────────────────────────────────────────────────────
        if platform == "GitHub":
            _gh_text = lambda sel: (soup.select_one(sel) or {}).get_text(strip=True) if soup.select_one(sel) else ""
            detail["display_name"] = _gh_text(".p-name") or _gh_text("h1.vcard-fullname")
            detail["bio"]          = _gh_text(".p-note") or _gh_text(".user-profile-bio")
            detail["company"]      = _gh_text(".p-org")
            detail["location"]     = _gh_text(".p-label")
            detail["website"]      = _gh_text(".p-url a") or _gh_text("a[itemprop='url']")
            # follower / following counts
            for a in soup.select("a[href*='?tab=followers'], a[href$='/followers']"):
                t = a.get_text(strip=True)
                if re.search(r'\d', t):
                    detail["followers"] = re.sub(r'\s+', ' ', t)
                    break
            # repos
            repo_tag = soup.select_one("span[class*='Counter'][id*='repositories']")
            if not repo_tag:
                for a in soup.select("a[href*='?tab=repositories']"):
                    s = a.select_one("span")
                    if s: repo_tag = s; break
            if repo_tag: detail["public_repos"] = repo_tag.get_text(strip=True)
            detail["links_in_bio"] = _extract_bio_links(detail.get("bio", "") + " " + detail.get("website", ""))
            return {k: v for k, v in detail.items() if v}

        # ── Instagram ───────────────────────────────────────────────────────
        if platform == "Instagram":
            # Meta description often: "123K Followers, 456 Following, 789 Posts - See Instagram…"
            og_desc = ""
            for sel in ['meta[property="og:description"]', 'meta[name="description"]']:
                t = soup.select_one(sel)
                if t and t.get("content"):
                    og_desc = t["content"].strip()
                    break
            if og_desc:
                detail["bio_meta"] = og_desc[:200]
                m = re.search(r'([\d,.KkMm]+)\s*Followers', og_desc, re.I)
                if m: detail["followers"] = m.group(1)
                m = re.search(r'([\d,.KkMm]+)\s*Following', og_desc, re.I)
                if m: detail["following"] = m.group(1)
                m = re.search(r'([\d,.KkMm]+)\s*Posts', og_desc, re.I)
                if m: detail["posts"] = m.group(1)
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["display_name"] = og_title.get("content", "").split("(")[0].strip()
            # Try window._sharedData JSON
            for script in soup.find_all("script"):
                t = script.string or ""
                if "window._sharedData" in t:
                    m = re.search(r'window\._sharedData\s*=\s*(\{.+?\});</script', t, re.S)
                    if m:
                        try:
                            sd = json.loads(m.group(1))
                            user = (sd.get("entry_data", {}).get("ProfilePage", [{}])[0]
                                    .get("graphql", {}).get("user", {}))
                            if user:
                                detail["full_name"]   = user.get("full_name", "")
                                detail["bio"]         = user.get("biography", "")[:200]
                                detail["followers"]   = str(user.get("edge_followed_by", {}).get("count", ""))
                                detail["following"]   = str(user.get("edge_follow", {}).get("count", ""))
                                detail["posts"]       = str(user.get("edge_owner_to_timeline_media", {}).get("count", ""))
                                detail["external_url"]= user.get("external_url", "")
                                detail["is_private"]  = str(user.get("is_private", ""))
                                detail["is_verified"] = str(user.get("is_verified", ""))
                        except Exception:
                            pass
                    break
            detail["links_in_bio"] = _extract_bio_links(detail.get("bio", "") + " " + detail.get("external_url", ""))
            return {k: v for k, v in detail.items() if v}

        # ── TikTok ──────────────────────────────────────────────────────────
        if platform == "TikTok":
            og_desc = ""
            for sel in ['meta[property="og:description"]', 'meta[name="description"]']:
                t = soup.select_one(sel)
                if t and t.get("content"):
                    og_desc = t["content"].strip(); break
            if og_desc: detail["bio_meta"] = og_desc[:200]
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["display_name"] = og_title.get("content", "").split("|")[0].strip()
            # SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
            for script in soup.find_all("script", id=re.compile(r'SIGI_STATE|__UNIVERSAL')):
                try:
                    d = json.loads(script.string or "")
                    # navigate: UserModule > users > {username}
                    users = (d.get("UserModule") or d.get("__DEFAULT_SCOPE__", {})
                             .get("webapp.user-detail", {}).get("userInfo", {}))
                    user  = (users.get("users", {}).get(username.lower(), {}) if isinstance(users, dict) else {})
                    stats = (d.get("UserModule", {}).get("stats", {}).get(username.lower(), {})
                             or (users.get("stats", {}) if isinstance(users, dict) else {}))
                    if user or stats:
                        detail["nickname"]  = user.get("nickname", "")
                        detail["bio"]       = user.get("signature", "")[:200]
                        detail["verified"]  = str(user.get("verified", ""))
                        detail["followers"] = str(stats.get("followerCount", ""))
                        detail["following"] = str(stats.get("followingCount", ""))
                        detail["likes"]     = str(stats.get("heartCount", ""))
                        detail["videos"]    = str(stats.get("videoCount", ""))
                    break
                except Exception:
                    pass
            detail["links_in_bio"] = _extract_bio_links(detail.get("bio", ""))
            return {k: v for k, v in detail.items() if v}

        # ── Twitter / X ─────────────────────────────────────────────────────
        if platform == "Twitter":
            og_desc = ""
            for sel in ['meta[property="og:description"]', 'meta[name="description"]']:
                t = soup.select_one(sel)
                if t and t.get("content"):
                    og_desc = t["content"].strip(); break
            if og_desc: detail["bio"] = og_desc[:200]
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["display_name"] = og_title.get("content", "").split("(")[0].strip()
            detail["links_in_bio"] = _extract_bio_links(og_desc)
            return {k: v for k, v in detail.items() if v}

        # ── Steam ────────────────────────────────────────────────────────────
        if platform == "Steam":
            detail["display_name"] = (soup.select_one(".actual_persona_name") or soup.select_one(".personaname") or type("", (), {"get_text": lambda *a, **k: ""})()).get_text(strip=True)
            real = soup.select_one(".profile_real_name")
            if real: detail["real_name"] = real.get_text(strip=True)
            loc = soup.select_one(".header_real_name .profile_flag")
            if not loc: loc = soup.select_one(".profile_location")
            if loc: detail["location"] = loc.get_text(strip=True)
            summary = soup.select_one(".profile_summary")
            if summary: detail["bio"] = summary.get_text(strip=True)[:200]
            level = soup.select_one(".friendPlayerLevelNum")
            if level: detail["steam_level"] = level.get_text(strip=True)
            friends = soup.select_one(".profile_friend_links a")
            if friends:
                m = re.search(r'(\d+)', friends.get_text())
                if m: detail["friends"] = m.group(1)
            badges = soup.select_one(".profile_badges_badge_count")
            if badges: detail["badges"] = badges.get_text(strip=True)
            detail["links_in_bio"] = _extract_bio_links(detail.get("bio", ""))
            return {k: v for k, v in detail.items() if v}

        # ── YouTube ──────────────────────────────────────────────────────────
        if platform == "YouTube":
            og_desc = ""
            for sel in ['meta[property="og:description"]', 'meta[name="description"]']:
                t = soup.select_one(sel)
                if t and t.get("content"):
                    og_desc = t["content"].strip(); break
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["channel_name"] = og_title.get("content", "").strip()
            if og_desc: detail["description"] = og_desc[:200]
            # ytInitialData
            for script in soup.find_all("script"):
                t = script.string or ""
                if "ytInitialData" in t:
                    m = re.search(r'var ytInitialData\s*=\s*(\{.+?\});\s*</script', t, re.S)
                    if not m:
                        m = re.search(r'ytInitialData\s*=\s*(\{.+)', t, re.S)
                    if m:
                        try:
                            yd = json.loads(m.group(1).rstrip(";"))
                            header = (yd.get("header", {}).get("c4TabbedHeaderRenderer")
                                      or yd.get("header", {}).get("pageHeaderRenderer", {}))
                            if isinstance(header, dict):
                                detail["channel_name"] = header.get("title", detail.get("channel_name", ""))
                                sc = header.get("subscriberCountText", {})
                                if isinstance(sc, dict):
                                    detail["subscribers"] = sc.get("simpleText", "") or "".join(r.get("text","") for r in sc.get("runs",[]))
                                desc_runs = (header.get("description", {}).get("channelDescriptionExpandableStringRenderer", {})
                                             .get("descriptionBodyText", {}).get("runs", []))
                                if desc_runs:
                                    detail["description"] = "".join(r.get("text","") for r in desc_runs)[:200]
                        except Exception:
                            pass
                    break
            detail["links_in_bio"] = _extract_bio_links(detail.get("description", ""))
            return {k: v for k, v in detail.items() if v}

        # ── Twitch ───────────────────────────────────────────────────────────
        if platform == "Twitch":
            og_desc = ""
            for sel in ['meta[property="og:description"]', 'meta[name="description"]']:
                t = soup.select_one(sel)
                if t and t.get("content"):
                    og_desc = t["content"].strip(); break
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["display_name"] = og_title.get("content", "").strip()
            if og_desc: detail["description"] = og_desc[:200]
            return {k: v for k, v in detail.items() if v}

        # ── Keybase ──────────────────────────────────────────────────────────
        if platform == "Keybase":
            for script in soup.find_all("script"):
                t = script.string or ""
                if '"them"' in t or '"basics"' in t:
                    m = re.search(r'\{.+\}', t, re.S)
                    if m:
                        try:
                            d = json.loads(m.group(0))
                            them = d.get("them", [{}])
                            them = them[0] if isinstance(them, list) and them else them
                            basics = them.get("basics", {}) if isinstance(them, dict) else {}
                            detail["username"]   = basics.get("username", "")
                            detail["created_at"] = basics.get("ctime", "")
                            proofs = them.get("proofs_summary", {}).get("all", []) if isinstance(them, dict) else []
                            for p in proofs[:6]:
                                detail[f"proof_{p.get('proof_type','')}"] = p.get("nametag", "")
                        except Exception:
                            pass
                    break
            return {k: v for k, v in detail.items() if v}

        # ── Linktree ─────────────────────────────────────────────────────────
        if platform == "Linktree":
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["display_name"] = og_title.get("content", "").strip()
            og_desc = soup.select_one('meta[property="og:description"]')
            if og_desc: detail["bio"] = og_desc.get("content", "").strip()[:200]
            links = []
            for a in soup.select("a[href]"):
                href = a.get("href", "")
                if href.startswith("http") and "linktr.ee" not in href:
                    txt = a.get_text(strip=True)
                    if txt and len(txt) > 2:
                        links.append(f"{txt}: {href}")
            if links: detail["links"] = " | ".join(links[:8])
            detail["links_in_bio"] = _extract_bio_links(" ".join(links))
            return {k: v for k, v in detail.items() if v}

        # ── Medium ────────────────────────────────────────────────────────────
        if platform == "Medium":
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title: detail["display_name"] = og_title.get("content", "").split("|")[0].strip()
            og_desc = soup.select_one('meta[property="og:description"]')
            if og_desc: detail["bio"] = og_desc.get("content", "").strip()[:200]
            return {k: v for k, v in detail.items() if v}

        # ── Generic fallback ─────────────────────────────────────────────────
        og_desc = ""
        for sel in ['meta[property="og:description"]', 'meta[name="description"]']:
            t = soup.select_one(sel)
            if t and t.get("content"):
                og_desc = t["content"].strip()
                if og_desc and len(og_desc) > 3:
                    detail["bio"] = og_desc[:200]
                    break
        og_title = soup.select_one('meta[property="og:title"]')
        if og_title:
            t = og_title.get("content", "").strip()
            if t and username.lower() not in t.lower()[:5]:
                detail["display_name"] = t.split("|")[0].split("•")[0].strip()[:60]
        detail["links_in_bio"] = _extract_bio_links(og_desc)
        return {k: v for k, v in detail.items() if v}

    except Exception:
        return {}


def _extract_bio_links(text: str) -> str:
    """
    Extract platform profile URLs and @mentions from any bio/description text.
    Returns a comma-separated string of discovered cross-platform handles.
    """
    if not text:
        return ""
    found = []

    # Direct URLs pointing to known platforms
    _url_patterns = [
        ("Instagram",   r'instagram\.com/([A-Za-z0-9_.]{1,30})'),
        ("Twitter",     r'(?:twitter|x)\.com/([A-Za-z0-9_]{1,15})'),
        ("TikTok",      r'tiktok\.com/@([A-Za-z0-9_.]{1,24})'),
        ("YouTube",     r'youtube\.com/(?:@|c/|channel/)([A-Za-z0-9_.]{1,30})'),
        ("GitHub",      r'github\.com/([A-Za-z0-9\-]{1,39})'),
        ("Reddit",      r'reddit\.com/u(?:ser)?/([A-Za-z0-9_]{1,20})'),
        ("Twitch",      r'twitch\.tv/([A-Za-z0-9_]{4,25})'),
        ("LinkedIn",    r'linkedin\.com/in/([A-Za-z0-9\-]{3,100})'),
        ("Snapchat",    r'snapchat\.com/add/([A-Za-z0-9_.]{1,30})'),
    ]
    _skip = {"search", "login", "signup", "help", "about", "explore", "home"}

    for plat, pat in _url_patterns:
        for m in re.finditer(pat, text, re.I):
            u = m.group(1).rstrip("/")
            if u.lower() not in _skip:
                found.append(f"{plat}:@{u}")

    # Bare @mentions that look like platform tags (e.g. "IG: @johndoe")
    for m in re.finditer(r'(?:ig|insta|instagram)[:\s]+@?([A-Za-z0-9_.]{2,30})', text, re.I):
        found.append(f"Instagram:@{m.group(1)}")
    for m in re.finditer(r'(?:tw|twitter|twt)[:\s]+@?([A-Za-z0-9_]{2,15})', text, re.I):
        found.append(f"Twitter:@{m.group(1)}")
    for m in re.finditer(r'(?:yt|youtube)[:\s]+@?([A-Za-z0-9_.]{2,30})', text, re.I):
        found.append(f"YouTube:@{m.group(1)}")
    for m in re.finditer(r'(?:snap)[:\s]+@?([A-Za-z0-9_.]{2,30})', text, re.I):
        found.append(f"Snapchat:@{m.group(1)}")

    # Also pull raw http(s) URLs for any platform not matched above
    for m in re.finditer(r'https?://[^\s"\'<>]{8,100}', text, re.I):
        url = m.group(0).rstrip(".,;)")
        already = any(url.lower() in f.lower() for f in found)
        if not already and not any(x in url.lower() for x in ("google.", "apple.", "mailto:")):
            found.append(url)

    # Deduplicate
    seen = set()
    result = []
    for f in found:
        key = f.lower()
        if key not in seen:
            seen.add(key)
            result.append(f)

    return "  |  ".join(result[:10]) if result else ""


def _format_found(label, value, indent=0):
    prefix = " " * indent + "↳"
    return f"{Fore.RED}{prefix} {Fore.WHITE}{label:<18}{Fore.LIGHTBLACK_EX}: {Fore.LIGHTCYAN_EX}{value}{Style.RESET_ALL}"

def _format_status(label, found, url="", indent=0):
    prefix = " " * indent + "↳"
    if found is True:
        badge = f"{Fore.GREEN}[FOUND]{Style.RESET_ALL}"
    elif found is False:
        badge = f"{Fore.RED}[NOT FOUND]{Style.RESET_ALL}"
    else:
        badge = f"{Fore.YELLOW}[TIMEOUT]{Style.RESET_ALL}"
    name_col = f"{Fore.WHITE}{label:<16}{Style.RESET_ALL}"
    url_col  = f"{Fore.LIGHTBLACK_EX}{url[:55]:<55}{Style.RESET_ALL}" if url and found else " " * 55
    return f"{Fore.RED}{prefix} {name_col} {badge}  {url_col}"


class SmartPersonLookup:
    """
    Smart OSINT person lookup.

    For a full name input, searches DuckDuckGo HTML to extract real linked
    usernames (e.g. the actual TikTok handle associated with "John Smith")
    rather than blindly guessing patterns like "johnsmith".  Confirmed
    usernames are then swept across 55+ platforms concurrently.

    Supports: username, full name, email address, phone number.
    """

    _SKIP_USERNAMES = {"search", "explore", "login", "signup", "register",
                       "home", "about", "privacy", "terms", "help", "support",
                       "twitter", "instagram", "tiktok", "youtube", "reddit"}

    def lookup(self, query: str, query_type: str = "auto", on_result=None,
               cascade: bool = True, max_cascade: int = 2):
        """
        Run a full OSINT sweep with optional chain discovery and contact extraction.

        on_result: optional callback(platform, url, found, detail, username, confidence)
          Special platform values:
            "__status__"  — status message in `confidence` field
            "__phase__"   — phase-transition message in `confidence` field

        Returns dict: query, query_type, candidates, found[], not_found[], errors[],
                      total, contacts{emails,phones}, cascade_usernames[]
        """
        if query_type == "auto":
            query_type = self._detect_type(query)

        candidates = self._build_candidates(query, query_type, on_result)

        # Phase 1: initial sweep
        sweep = self._run_sweep(candidates, on_result)
        all_found = sweep["found"]
        all_checked = {u.lower() for u, _ in candidates}
        cascade_usernames = []

        # Phase 2+: cascade through bio links (up to max_cascade levels)
        if cascade:
            for _level in range(max_cascade):
                new_usernames = self._parse_cascade_usernames(all_found, all_checked)
                if not new_usernames:
                    break
                if on_result:
                    preview = ", ".join(new_usernames[:3])
                    on_result("__phase__", "", None, None, "",
                              f"Found {len(new_usernames)} linked account(s) in bios → {preview}")
                cascade_usernames.extend(new_usernames)
                all_checked.update(u.lower() for u in new_usernames)

                extra = self._run_sweep([(u, "bio-link") for u in new_usernames], on_result)
                found_platforms = {e["platform"] for e in all_found}
                for entry in extra["found"]:
                    if entry["platform"] not in found_platforms:
                        all_found.append(entry)
                        found_platforms.add(entry["platform"])

        # Specialized intelligence for email / phone / domain
        intel_data = {}
        if query_type == "email":
            if on_result:
                on_result("__status__", "", None, None, "",
                          "Running breach & reputation checks…")
            try:
                from .intel import breach_check, gravatar_lookup
                intel_data["breach"]   = breach_check(query)
                intel_data["gravatar"] = gravatar_lookup(query)
            except Exception:
                pass

        elif query_type == "phone":
            if on_result:
                on_result("__status__", "", None, None, "",
                          "Enriching phone number…")
            try:
                from .intel import phone_enrich
                intel_data["phone"] = phone_enrich(query)
            except Exception:
                pass

        # Person: paste-site leak search
        if query_type in ("username", "name", "email"):
            if on_result:
                on_result("__status__", "", None, None, "",
                          "Scanning paste sites for leaked data…")
            try:
                from .intel import paste_search
                hits = paste_search(query)
                if hits:
                    intel_data["paste_hits"] = hits
            except Exception:
                pass

        # Extract contacts from all gathered profile data
        contacts = self._extract_contacts(all_found)

        from .platforms import get_platforms, get_platform_count
        all_platform_names = set(get_platforms().keys())
        found_platforms    = {e["platform"] for e in all_found}
        return {
            "query":             query,
            "query_type":        query_type,
            "candidates":        candidates,
            "found":             sorted(all_found, key=lambda x: x["platform"]),
            "not_found":         [{"platform": p} for p in sorted(all_platform_names)
                                  if p not in found_platforms],
            "errors":            [],
            "total":             get_platform_count(),
            "contacts":          contacts,
            "cascade_usernames": cascade_usernames,
            "intel":             intel_data,
        }

    # ── internal sweep helper ───────────────────────────────────────────────

    def _run_sweep(self, candidates, on_result):
        """Sweep all platforms for the given (username, confidence) candidates."""
        from .platforms import get_platforms
        all_platforms = get_platforms()   # merged Sherlock + our deep-scrapers
        seen_results  = {}

        for username, confidence in candidates:
            with ThreadPoolExecutor(max_workers=30) as pool:
                futures = {
                    pool.submit(
                        _check_platform,
                        name, probe_url, rule, username, 8, disp_url
                    ): name
                    for name, (probe_url, rule, disp_url) in all_platforms.items()
                }
                for future in as_completed(futures):
                    platform, url, found, detail = future.result()
                    if found is True:
                        prev = seen_results.get(platform)
                        if not prev or confidence in ("web-confirmed", "bio-link"):
                            seen_results[platform] = {
                                "platform": platform,
                                "url": url,
                                "detail": detail,
                                "username": username,
                                "confidence": confidence,
                            }
                        if on_result:
                            on_result(platform, url, found, detail, username, confidence)
                    elif found is False and platform not in seen_results:
                        if on_result:
                            on_result(platform, url, found, detail, username, confidence)
                    elif found is None:
                        if on_result:
                            on_result(platform, url, found, detail, username, confidence)

        found = sorted(seen_results.values(), key=lambda x: x["platform"])
        found_platforms = {e["platform"] for e in found}
        return {
            "found":     found,
            "not_found": [{"platform": p} for p in sorted(all_platforms.keys())
                          if p not in found_platforms],
        }

    # ── cascade helpers ─────────────────────────────────────────────────────

    def _parse_cascade_usernames(self, found_profiles: list, already_checked: set) -> list:
        """Extract new usernames from links_in_bio across all found profiles."""
        new = []
        seen = set()
        for entry in found_profiles:
            detail = entry.get("detail") or {}
            links_text = detail.get("links_in_bio", "")
            if not links_text:
                continue
            for part in links_text.split("|"):
                part = part.strip()
                m = re.match(r'[A-Za-z0-9 .]+:@([A-Za-z0-9_.]{2,30})$', part)
                if m:
                    u = m.group(1)
                    ul = u.lower()
                    if ul not in already_checked and ul not in seen and ul not in self._SKIP_USERNAMES:
                        seen.add(ul)
                        new.append(u)
        return new

    @staticmethod
    def _extract_contacts(found_profiles: list) -> dict:
        """Extract email addresses and phone numbers from all scraped profile text."""
        chunks = []
        for entry in found_profiles:
            detail = entry.get("detail") or {}
            for k, v in detail.items():
                if v and k != "links_in_bio":
                    chunks.append(str(v))
        text = " ".join(chunks)

        emails = set()
        for m in re.finditer(r'[\w.+-]{2,}@[\w-]+\.\w{2,}', text):
            e = m.group(0)
            blocklist = ("example.", "noreply", "no-reply", "support@",
                         "@sentry", "@github", "@gravatar", "@wp.")
            if not any(x in e.lower() for x in blocklist):
                emails.add(e)

        phones = set()
        # International: +xx xxx xxx xxxx
        for m in re.finditer(r'\+\d{1,3}[\s.\-]?\(?\d{2,4}\)?[\s.\-]?\d{3,4}[\s.\-]?\d{3,4}', text):
            p = m.group(0).strip()
            if len(re.sub(r'\D', '', p)) >= 7:
                phones.add(p)
        # US format (xxx) xxx-xxxx
        for m in re.finditer(r'(?<!\d)\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)', text):
            p = m.group(0).strip()
            if len(re.sub(r'\D', '', p)) == 10:
                phones.add(p)

        return {"emails": list(emails), "phones": list(phones)}

    # ── candidate generation ────────────────────────────────────────────────

    def _build_candidates(self, query: str, query_type: str, on_result):
        """Return [(username, confidence), ...] deduped, web-confirmed first."""
        candidates = []

        if query_type == "username":
            candidates.append((query.lstrip("@"), "web-confirmed"))

        elif query_type == "email":
            local = query.split("@")[0]
            candidates.append((local, "web-confirmed"))
            candidates += [(u, "pattern") for u in self._name_variants(local)]

        elif query_type == "phone":
            candidates += self._web_hunt(query, phone=True)

        elif query_type == "name":
            # 1. Web-hunt for real usernames linked to this name
            if on_result:
                on_result("__status__", "", None, None, query, "Searching web for linked usernames…")
            web_hits = self._web_hunt_name(query)
            candidates += [(u, "web-confirmed") for u in web_hits]

            # 2. Pattern variants as fallback
            parts = query.lower().split()
            if len(parts) >= 2:
                first, last = parts[0], parts[-1]
                candidates += [(u, "pattern") for u in self._name_variants_fl(first, last)]

        # Deduplicate, preserve order, web-confirmed before pattern
        seen = set()
        deduped = []
        for username, conf in sorted(candidates, key=lambda x: 0 if x[1] == "web-confirmed" else 1):
            u = username.lower()
            if u and u not in seen and u not in self._SKIP_USERNAMES and len(u) >= 2:
                seen.add(u)
                deduped.append((username, conf))

        return deduped[:8]  # cap at 8 candidates to keep scan time reasonable

    def _web_hunt_name(self, name: str) -> list:
        """Query DuckDuckGo HTML for each major platform and extract real usernames."""
        found = []
        platforms_to_hunt = [
            ("Twitter",   r'(?:twitter|x)\.com/([A-Za-z0-9_]{1,15})(?:/|\?|$|\s)',    "twitter.com"),
            ("Instagram", r'instagram\.com/([A-Za-z0-9_.]{1,30})(?:/|\?|$|\s)',        "instagram.com"),
            ("TikTok",    r'tiktok\.com/@([A-Za-z0-9_.]{1,24})(?:/|\?|$|\s)',          "tiktok.com"),
            ("YouTube",   r'youtube\.com/@([A-Za-z0-9_.]{1,30})(?:/|\?|$|\s)',         "youtube.com"),
            ("Reddit",    r'reddit\.com/u(?:ser)?/([A-Za-z0-9_\-]{3,20})(?:/|\?|$|\s)', "reddit.com"),
            ("GitHub",    r'github\.com/([A-Za-z0-9\-]{1,39})(?:/|\?|$|\s)',           "site:github.com"),
            ("LinkedIn",  r'linkedin\.com/in/([A-Za-z0-9\-]{3,100})(?:/|\?|$|\s)',     "linkedin.com"),
        ]

        quoted = f'"{name}"'
        for plat_name, pattern, site_hint in platforms_to_hunt:
            try:
                q = quote_plus(f'{quoted} site:{site_hint}')
                r = requests.get(
                    _DDG_SEARCH_URL.format(q),
                    headers=_SESSION_HEADERS,
                    timeout=10,
                )
                soup = BeautifulSoup(r.text, 'html.parser')
                text = r.text

                # Extract from href attributes (most reliable)
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    m = re.search(pattern, href, re.IGNORECASE)
                    if m:
                        u = m.group(1)
                        if u.lower() not in self._SKIP_USERNAMES and len(u) >= 2:
                            found.append(u)

                # Also scan raw text for patterns (catches redirected DDG links)
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    u = m.group(1)
                    if u.lower() not in self._SKIP_USERNAMES and len(u) >= 2:
                        found.append(u)

                time.sleep(0.5)  # be polite to DDG
            except Exception:
                pass

        # Deduplicate while preserving order
        seen = set()
        result = []
        for u in found:
            if u.lower() not in seen:
                seen.add(u.lower())
                result.append(u)
        return result

    @staticmethod
    def _name_variants_fl(first: str, last: str) -> list:
        """Generate common username patterns from first+last name."""
        variants = [
            f"{first}{last}",
            f"{first}.{last}",
            f"{first}_{last}",
            f"{last}{first}",
            f"{first[0]}{last}",
            f"{first}{last[0]}",
            f"{first}.{last[0]}",
            f"{first[0]}.{last}",
            f"{first}{last[:3]}",
        ]
        return list(dict.fromkeys(v for v in variants if len(v) >= 3))

    @staticmethod
    def _name_variants(name: str) -> list:
        """Variants from a single name token (e.g. email local part)."""
        return [name, name.replace(".", ""), name.replace("_", ""), name.replace("-", "")]

    @staticmethod
    def _web_hunt(query: str, phone: bool = False) -> list:
        """Generic DDG search for any query, return (username, confidence) pairs."""
        candidates = []
        try:
            q = quote_plus(f'"{query}"')
            r = requests.get(_DDG_SEARCH_URL.format(q), headers=_SESSION_HEADERS, timeout=10)
            for plat_name, (pattern, site) in _PLATFORM_WEB_PATTERNS.items():
                for m in re.finditer(pattern, r.text, re.IGNORECASE):
                    u = m.group(1)
                    candidates.append((u, "web-confirmed"))
        except Exception:
            pass
        return candidates

    # ── type detection ──────────────────────────────────────────────────────

    @staticmethod
    def _detect_type(query: str) -> str:
        if re.match(r'^[+\d\s\-().]{7,15}$', query):
            return "phone"
        if re.match(r'^[\w.+-]+@[\w-]+\.\w+$', query):
            return "email"
        if " " in query:
            return "name"
        return "username"

    # ── report printer ──────────────────────────────────────────────────────

    @staticmethod
    def print_report(results, show_not_found=False):
        q  = results["query"]
        qt = results["query_type"]
        found = results["found"]
        err   = results.get("errors", [])
        cands = results.get("candidates", [])

        print(f"\n{Fore.RED}{'═' * 72}{Style.RESET_ALL}")
        print(f"{Fore.RED}  OSINT PROFILE REPORT{Style.RESET_ALL}")
        print(f"{Fore.RED}{'═' * 72}{Style.RESET_ALL}\n")
        print(_format_found("Query",              q,                            indent=1))
        print(_format_found("Type",               qt,                           indent=1))
        print(_format_found("Platforms checked",  str(results["total"]),        indent=1))
        print(_format_found("Accounts found",     f"{Fore.GREEN}{len(found)}{Style.RESET_ALL}", indent=1))

        confirmed = [u for u, c in cands if c == "web-confirmed"]
        patterns  = [u for u, c in cands if c == "pattern"]
        if confirmed:
            print(_format_found("Web-confirmed IDs",  ", ".join(confirmed),     indent=1))
        if patterns:
            print(_format_found("Pattern candidates",  ", ".join(patterns),     indent=1))
        print()

        if found:
            print(f"{Fore.RED}  ── FOUND ACCOUNTS {'─' * 50}{Style.RESET_ALL}")
            for entry in found:
                conf_badge = (
                    f"{Fore.GREEN}[✓ web]{Style.RESET_ALL}"
                    if entry.get("confidence") == "web-confirmed"
                    else f"{Fore.YELLOW}[~ pat]{Style.RESET_ALL}"
                )
                uname = entry.get("username", "")
                print(f"  {Fore.RED}↳ {Fore.WHITE}{entry['platform']:<16}{Style.RESET_ALL} "
                      f"{conf_badge} {Fore.LIGHTBLACK_EX}as {Fore.LIGHTCYAN_EX}{uname:<20}{Style.RESET_ALL} "
                      f"{Fore.LIGHTBLACK_EX}{entry['url'][:48]}{Style.RESET_ALL}")
                if entry.get("detail"):
                    for k, v in entry["detail"].items():
                        if v:
                            print(f"     {Fore.LIGHTBLACK_EX}└─ {k}: {Fore.LIGHTCYAN_EX}{v}{Style.RESET_ALL}")
            print()

        if show_not_found and results.get("not_found"):
            print(f"{Fore.RED}  ── NOT FOUND {'─' * 55}{Style.RESET_ALL}")
            for entry in results["not_found"]:
                print(_format_status(entry["platform"], False, indent=2))
            print()

        if err:
            platforms = ", ".join(e["platform"] for e in err)
            print(f"{Fore.YELLOW}  ↳ Timeout/error on: {platforms}{Style.RESET_ALL}\n")

        print(f"{Fore.RED}{'═' * 72}{Style.RESET_ALL}\n")


# Keep old name as alias so existing imports don't break
PersonProfiler = SmartPersonLookup


class EmailFinder:
    """Email address discovery tool"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(_SESSION_HEADERS)

    def find_emails(self, domain):
        emails = set()
        ColorPrinter.info(f"Searching for emails from {domain}")
        email_pattern = re.compile(r'[\w\.-]+@' + re.escape(domain), re.IGNORECASE)

        sources = [
            f"https://www.google.com/search?q=site:{domain}+email",
            f"https://www.google.com/search?q=site:{domain}+contact",
        ]
        for source in sources:
            try:
                response = self.session.get(source, timeout=10)
                emails.update(email_pattern.findall(response.text))
                time.sleep(1)
            except Exception as e:
                ColorPrinter.warning(f"Error searching {source}: {str(e)[:50]}")

        for page in ['', 'contact', 'about', 'team']:
            try:
                url = f"http://{domain}/{page}" if page else f"http://{domain}"
                response = self.session.get(url, timeout=10)
                emails.update(email_pattern.findall(response.text))
                time.sleep(0.5)
            except Exception:
                pass

        return list(emails)


class SocialMediaSearch:
    """Social media profile discovery"""

    def search_profiles(self, name, company=None):
        profiles = {}
        ColorPrinter.info(f"Searching social media for: {name}")
        profiles['LinkedIn'] = f"https://www.linkedin.com/search/results/people/?keywords={name}"
        profiles['Twitter']  = f"https://twitter.com/search?q={name}&f=user"
        profiles['Facebook'] = f"https://www.facebook.com/search/people/?q={name}"
        profiles['GitHub']   = f"https://github.com/search?q={name}&type=users"
        profiles['Instagram'] = f"https://www.instagram.com/web/search/topsearch/?query={name}"
        return profiles


class DomainScraper:
    """Domain and subdomain enumeration"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(_SESSION_HEADERS)

    def scrape_subdomains(self, domain):
        subdomains = set()
        ColorPrinter.info(f"Scraping subdomains for {domain}")

        for url in [f"https://crt.sh/?q=%25.{domain}", ]:
            try:
                response = self.session.get(url, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if domain in href and '://' not in href:
                        sub = href.split('?')[0].strip()
                        if sub.endswith('.' + domain):
                            subdomains.add(sub)
                time.sleep(1)
            except Exception as e:
                ColorPrinter.warning(f"Error scraping {url}: {str(e)[:50]}")

        common = ['www', 'mail', 'ftp', 'smtp', 'pop', 'ns1', 'ns2', 'webmail',
                  'm', 'imap', 'test', 'dev', 'api', 'cdn', 'admin', 'blog',
                  'vpn', 'staging', 'beta', 'shop', 'secure', 'portal']
        ColorPrinter.info("Testing common subdomains...")
        for sub in common:
            try:
                socket.gethostbyname(f"{sub}.{domain}")
                subdomains.add(f"{sub}.{domain}")
                print(f"  Found: {sub}.{domain}")
            except Exception:
                pass

        return list(subdomains)


class MetadataExtractor:
    """Extract metadata from files and websites"""

    def extract_from_url(self, url):
        metadata = {}
        ColorPrinter.info(f"Extracting metadata from {url}")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.text.strip()
            for tag in soup.find_all('meta'):
                name = tag.get('name') or tag.get('property')
                content = tag.get('content')
                if name and content:
                    metadata[name] = content
            metadata['links']  = [a['href'] for a in soup.find_all('a', href=True)[:10]]
            metadata['images'] = [i['src'] for i in soup.find_all('img', src=True)[:5]]
        except Exception as e:
            ColorPrinter.error(f"Error extracting metadata: {str(e)}")
        return metadata

    def extract_from_file(self, file_path):
        metadata = {}
        try:
            import os
            stat = os.stat(file_path)
            metadata['size']     = stat.st_size
            metadata['modified'] = time.ctime(stat.st_mtime)
            metadata['created']  = time.ctime(stat.st_ctime)
        except Exception as e:
            ColorPrinter.error(f"Error reading file: {str(e)}")
        return metadata


# ── convenience functions ────────────────────────────────────────────────────

def find_emails(domain):
    return EmailFinder().find_emails(domain)

def search_social_media(name, company=None):
    return SocialMediaSearch().search_profiles(name, company)

def scrape_subdomains(domain):
    return DomainScraper().scrape_subdomains(domain)

def extract_metadata(url_or_file):
    extractor = MetadataExtractor()
    if url_or_file.startswith(('http://', 'https://')):
        return extractor.extract_from_url(url_or_file)
    return extractor.extract_from_file(url_or_file)
