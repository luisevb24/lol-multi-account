import json
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
UA_STRING = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def riot_get_json(url, api_key):
    req = Request(url, method="GET")
    req.add_header("User-Agent", UA_STRING)
    req.add_header("Accept", "application/json")
    req.add_header("Accept-Language", "en-US,en;q=0.9")
    req.add_header("X-Riot-Token", api_key)
    try:
        with urlopen(req) as resp: 
            raw = resp.read()
            text = raw.decode("utf-8")
            data = json.loads(text)
        return data
    except HTTPError as e: 
        status = e.code
        body = e.read().decode("utf-8", errors="replace")
        if status == 401:
            raise RuntimeError("401 Unauthorized: Check your RIOT_API_KEY (expired or invalid).")
        elif status == 403:
            raise RuntimeError("403 Unauthorized: Check your RIOT_API_KEY (expired or invalid).")
        elif status == 404:
            raise RuntimeError("Riot ID not found. Check summoner name, tag line, and routing.")
        elif status == 429:
            retry_after = e.headers.get("Retry-After", "unknown")
            raise RuntimeError(f"Rate limited by Riot API. Retry after {retry_after} seconds.")
        else:
            raise RuntimeError(f"Riot API error {status}: {body}")
    except URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")

def  platform_to_routing(platform: str):
    PLATFORM_TO_ROUTING = {
    "LA1": "americas",
    "LA2": "americas",
    "NA1": "americas",
    "BR1": "americas",
    "EUW1": "europe",
    "EUN1": "europe",
    "TR1": "europe",
    "RU": "europe",
    "KR": "asia",
    "JP1": "asia",
}
    platform = platform.upper()
    if platform not in PLATFORM_TO_ROUTING:
        raise ValueError(f"Unsupported region {platform}")
    return PLATFORM_TO_ROUTING[platform]

def platform_to_host(platform: str):
    PLATFORM_TO_ROUTING = {
    "LA1": "americas",
    "LA2": "americas",
    "NA1": "americas",
    "BR1": "americas",
    "EUW1": "europe",
    "EUN1": "europe",
    "TR1": "europe",
    "RU": "europe",
    "KR": "asia",
    "JP1": "asia",
}   
    if platform not in PLATFORM_TO_ROUTING:
        raise ValueError(f"Unsupported region {platform}")
    platform = platform.lower()
    host = f"https://{platform}.api.riotgames.com"
    return host

def get_account_by_riot_id(summoner_name, tag_line, routing, api_key):
    host = f"https://{routing}.api.riotgames.com"
    encoded_name = quote(summoner_name, safe="")
    encoded_tag = quote(tag_line, safe="")
    path = f"/riot/account/v1/accounts/by-riot-id/{encoded_name}/{encoded_tag}"
    url = host + path
    return riot_get_json(url, api_key)

def get_summoner_by_puuid(platform, puuid, api_key):
    host = platform_to_host(platform)
    path = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
    url = host + path
    return riot_get_json(url, api_key)

def get_ranked_entries(platform, puuid, api_key):
    host = platform_to_host(platform)
    path = f"/lol/league/v4/entries/by-puuid/{puuid}"
    url = host+path
    return riot_get_json(url, api_key)

def get_recent_match_ids(puuid, platform, api_key, count=5):
    routing = platform_to_routing(platform)
    host = f"https://{routing}.api.riotgames.com"
    path = f"/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    url = host + path
    return riot_get_json(url, api_key)

def get_match(match_id, platform, api_key):
    routing = platform_to_routing(platform)
    host = f"https://{routing}.api.riotgames.com"
    path = f"/lol/match/v5/matches/{match_id}"
    url = host + path
    return riot_get_json(url, api_key)

