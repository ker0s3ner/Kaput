"""
Platform database.

Downloads and caches Sherlock's community-maintained data.json (400+ sites),
converts it to our internal (url_template, check_rule) format, and merges it
with our hand-scraped platform list so deep scrapers take priority.
"""

import os
import json
import time
import requests

_CACHE_PATH = os.path.join(os.path.dirname(__file__), "_sherlock_cache.json")
_CACHE_TTL  = 7 * 24 * 3600  # refresh weekly
_SHERLOCK_URL = (
    "https://raw.githubusercontent.com/sherlock-project/sherlock/"
    "master/sherlock_project/resources/data.json"
)


# ── Our hand-scraped platforms (kept as-is; these are NOT overridden) ─────────
OUR_PLATFORMS = {
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
    "Slashdot":       ("https://slashdot.org/~{}",                    "status"),
    "SourceForge":    ("https://sourceforge.net/u/{}/profile/",       "status"),
    "Trello":         ("https://trello.com/{}",                       "status"),
    "Codecademy":     ("https://www.codecademy.com/profiles/{}",      "status"),
    "Freecodecamp":   ("https://www.freecodecamp.org/{}",             "status"),
}


def _sherlock_to_rule(cfg: dict) -> tuple:
    """Convert a Sherlock platform config to (url_template, check_rule)."""
    url  = cfg.get("urlProbe") or cfg.get("url", "")
    disp = cfg.get("url", url)
    et   = cfg.get("errorType", "status_code")

    if et == "status_code":
        rule = "status"
    elif et == "message":
        msg  = cfg.get("errorMsg", "")
        rule = f"not_content:{msg[:80]}"
    elif et == "profilePresence":
        msg  = cfg.get("errorMsg", "")
        rule = f"content:{msg[:80]}"
    elif et == "response_url":
        bad  = cfg.get("errorUrl", "")
        rule = f"url_not:{bad[:100]}"
    else:
        rule = "status"

    return (url, rule, disp)


def load_sherlock(timeout: int = 10) -> dict:
    """
    Download Sherlock's data.json (cached weekly).
    Returns the raw dict keyed by platform name.
    """
    if os.path.exists(_CACHE_PATH):
        if time.time() - os.path.getmtime(_CACHE_PATH) < _CACHE_TTL:
            try:
                with open(_CACHE_PATH) as f:
                    return json.load(f)
            except Exception:
                pass

    try:
        r = requests.get(_SHERLOCK_URL, timeout=timeout,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            data = r.json()
            try:
                with open(_CACHE_PATH, "w") as f:
                    json.dump(data, f)
            except Exception:
                pass
            return data
    except Exception:
        pass

    # Stale cache is better than nothing
    if os.path.exists(_CACHE_PATH):
        try:
            with open(_CACHE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def get_platforms(include_sherlock: bool = True) -> dict:
    """
    Return the merged platform dict: {name: (probe_url, check_rule, display_url)}.

    Our hand-scraped entries (OUR_PLATFORMS) always take priority over Sherlock.
    Sherlock entries only get a 2-tuple (url_template, check_rule) — display_url == url_template.
    """
    merged = {}

    if include_sherlock:
        raw = load_sherlock()
        for name, cfg in raw.items():
            if not isinstance(cfg, dict):
                continue
            url, rule, disp = _sherlock_to_rule(cfg)
            if not url:
                continue
            merged[name] = (url, rule, disp)

    # Our platforms override Sherlock — they have deep scrapers
    for name, (url, rule) in OUR_PLATFORMS.items():
        merged[name] = (url, rule, url)

    return merged


def get_platform_count(include_sherlock: bool = True) -> int:
    return len(get_platforms(include_sherlock))
