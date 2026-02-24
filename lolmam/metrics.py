from . import riot_client
import statistics

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"

def color_wr(wr: float) -> str:
    if wr >= 55:
        return f"{GREEN}{wr:.1f}%{RESET}"
    if wr >= 50:
        return f"{YELLOW}{wr:.1f}%{RESET}"
    return f"{RED}{wr:.1f}%{RESET}"


def extract_match_metrics(puuid: str, match: dict):
    player = None
    for p in match["info"]["participants"]:
        if p["puuid"] == puuid:
            player = p
    if not player:
        raise ValueError("Player not found")
    
    kills = player.get("kills", 0)
    deaths = player.get("deaths", 0)
    assists = player.get("assists", 0)
    win = bool(player.get("win", False))
    cs = player.get("totalMinionsKilled", 0) + player.get("neutralMinionsKilled", 0)
    seconds = player.get("timePlayed")
    if not seconds:
        seconds = match["info"].get("gameDuration")
    minutes = seconds / 60
    if minutes > 0:
        cs_per_min = cs / minutes
    else: 
        cs_per_min = 0.0

    role = player.get("teamPosition") or "UNKNOWN"

    champ = player.get("championName") or "UNKNOWN"

    metrics = {
        "win": win,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "cs": cs,
        "minutes": minutes, 
        "cs_per_min": cs_per_min,
        "role": role,
        "champ" : champ
    }

    return metrics

def compute_account_metrics(account: dict, api_key: str):
    platform = account["region"]
    puuid = account["puuid"]
    match_ids = riot_client.get_recent_match_ids(puuid, platform, api_key, 10)
    metrics = {
        "account_id": account["id"],
        "summoner_name": account["summoner_name"],
        "region": account["region"],
        "games": 0,
        "winrate": 0, 
        "avg_kda": 0,
        "avg_cs_min": 0,
        "most_played_role": "UNKNOWN",
    }
    if not match_ids: 
        return metrics
    #accumulators
    wins = 0
    kills_sum = 0
    deaths_sum = 0
    assists_sum = 0
    csmin_sum = 0
    roles = []
    champ_counts = {}

    for match_id in match_ids:
        match = riot_client.get_match(match_id, platform, api_key)
        m = extract_match_metrics(puuid, match)
        if m["win"]: 
            wins += 1
        kills_sum += m["kills"]
        deaths_sum += m["deaths"]
        assists_sum += m["assists"]
        csmin_sum += m["cs_per_min"]
        roles.append(m["role"])
        champ = m["champ"]
        champ_counts[champ] = champ_counts.get(champ, 0) + 1


    games = len(match_ids)
    winrate = wins / games * 100
    avg_cs_min = csmin_sum / games
    avg_kda = (kills_sum + assists_sum) / max(1, deaths_sum)
    most_played_role = statistics.mode(roles)

    metrics ={
        "account_id": account["id"],
        "summoner_name": account["summoner_name"],
        "region": account["region"],
        "games": games,
        "winrate": winrate, 
        "avg_kda": avg_kda,
        "avg_cs_min": avg_cs_min,
        "most_played_role": most_played_role,
        "wins": wins,
        "kills_sum": kills_sum,
        "deaths_sum": deaths_sum,
        "assists_sum": assists_sum,
        "csmin_sum": csmin_sum,
        "champ_counts": champ_counts,
    }

    return metrics

def compute_all_accounts_metrics(accounts, api_key):
    return [
        compute_account_metrics(acc, api_key)
        for acc in accounts
    ]

def compute_master_metrics(metrics_list):
    accounts = len(metrics_list)
    total_games = 0
    total_wins = 0
    kills_total = 0
    deaths_total = 0 
    assists_total = 0
    cs_min_total = 0.0 
    champ_counts_global = {}
    
    for m in metrics_list: 
        total_games += m["games"]
        total_wins += m["wins"]
        kills_total += m["kills_sum"]
        deaths_total += m["deaths_sum"]
        assists_total += m["assists_sum"]
        cs_min_total += m["csmin_sum"]
        champ_counts_global.update(m["champ_counts"])
    
    if total_games > 0:
        winrate = total_wins / total_games * 100
        kda = (kills_total + assists_total) / max(1, deaths_total)
        cs_min = cs_min_total / total_games
        top_champs = sorted(champ_counts_global.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "accounts": accounts,
        "matches": total_games, 
        "winrate": winrate,
        "kda": kda, 
        "cs_min": cs_min, 
        "top_champs": top_champs    
    }

def print_master_summary(master: dict, metrics_list: list[dict]) -> None:
    # Header
    print(f"\n{BOLD}MASTER ACCOUNT{RESET} (last 10 matches per account)")
    print(f"Accounts: {master['accounts']} | Matches analyzed: {master['matches']}\n")

    # Overall block
    print(f"{BOLD}Overall{RESET}")
    print(f"- Winrate: {master['winrate']:.1f}%")
    print(f"- KDA: {master['kda']:.2f}")
    print(f"- CS/min: {master['cs_min']:.2f}")

    # Top champs (global)
    top_champs = master.get("top_champs", [])
    if top_champs:
        champs_str = ", ".join([f"{name} ({count})" for name, count in top_champs])
        print(f"- Top champs: {champs_str}")
    else:
        print(f"- Top champs: None")

    print("\n" + f"{BOLD}Internal ranking (by winrate){RESET}")

    # Sort ranking by winrate desc (then KDA as tie-breaker)
    ranked = sorted(
        metrics_list,
        key=lambda m: (m.get("winrate", 0.0), m.get("avg_kda", 0.0)),
        reverse=True
    )

    if not ranked:
        print("No accounts to rank.")
        return

    # Build rows first for widths
    rows = []
    for i, m in enumerate(ranked, start=1):
        champ_counts = m.get("champ_counts", {})
        if champ_counts:
            top_champ = max(champ_counts, key=champ_counts.get)
        else:
            top_champ = "UNKNOWN"

        rows.append({
            "n": i,
            "name": f"{m.get('summoner_name', 'UNKNOWN')} ({m.get('region', '??')})",
            "wr": m.get("winrate", 0.0),
            "kda": m.get("avg_kda", 0.0),
            "cs": m.get("avg_cs_min", 0.0),
            "role": m.get("most_played_role", "UNKNOWN"),
            "champ": top_champ,
        })

    # Column widths (use uncolored strings for width calc)
    n_w = max(len("#"), max(len(str(r["n"])) for r in rows))
    name_w = max(len("Account"), max(len(r["name"]) for r in rows))
    wr_w = len("WR")
    kda_w = len("KDA")
    cs_w = len("CS/min")
    champ_w = max(len("Top champ"), max(len(r["champ"]) for r in rows))

    # Header line
    sep = "  "
    total_width = n_w + name_w + wr_w + kda_w + cs_w + champ_w + len(sep) * 6

    print("-" * total_width)
    print(
        f"{'#':<{n_w}}{sep}"
        f"{'Account':<{name_w}}{sep}"
        f"{'WR':>{wr_w}}{sep}"
        f"{'KDA':>{kda_w}}{sep}"
        f"{'CS/min':>{cs_w}}{sep}"
        f"{'Top champ':<{champ_w}}"
    )
    print("-" * total_width)

    for r in rows:
        wr_col = color_wr(r["wr"])
        # Note: wr_w is tiny; we align by printing the colored WR without strict padding
        # (ANSI codes break length calc). We keep columns readable anyway.

        print(
            f"{r['n']:<{n_w}}{sep}"
            f"{r['name']:<{name_w}}{sep}"
            f"{wr_col}{sep}"
            f"{r['kda']:>{kda_w}.2f}{sep}"
            f"{r['cs']:>{cs_w}.2f}{sep}"
            f"{r['champ']:<{champ_w}}"
        )

    print("-" * total_width)

    