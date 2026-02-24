import argparse
from . import storage
from .config import load_env
import os
from . import riot_client
from . import metrics
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
CYAN = "\033[36m"

def build_parser():
    parser = argparse.ArgumentParser(prog="lolmam", description="Register multiple lol accounts and get a summary of your stats")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_add = subparsers.add_parser("add-account", help="Register an account")
    p_add.add_argument("summoner_name", help="Summoner name")
    p_add.add_argument("tag_line", help="Tagline (ej: ABC)")
    p_add.add_argument("region", help="Region (ej: LA1)")

    p_list = subparsers.add_parser("list-accounts", help="List registered accounts")

    p_sum = subparsers.add_parser("summary", help="Summary of a given account")
    p_sum.add_argument("account_id", type=int, help="Numeric ID of the account")

    p_all = subparsers.add_parser("master-acc", help="Master account")
    return parser


def main(argv=None):
    load_env()
    parser = build_parser()
    args = parser.parse_args(argv)
    api_key = os.getenv("RIOT_API_KEY")
    if not api_key: 
        print("Error: RIOT_API_KEY not set. Create a .env file in the project root")
        return 1
    if args.command == "add-account":
        data = riot_client.get_account_by_riot_id(args.summoner_name, args.tag_line, riot_client.platform_to_routing(args.region), api_key)
        puuid = data["puuid"]
        storage.add_account(args.summoner_name, args.tag_line, args.region, puuid)
        print(f"Added account {args.summoner_name}#{args.tag_line} ({args.region})")
    elif args.command == "list-accounts":
        accounts = storage.list_accounts()
        if not accounts: 
            print("No accounts registered.")
        elif accounts: 
            id_width = max(len("ID"), max(len(str(acc["id"])) for acc in accounts))
            summoner_width = max(len("SUMMONER"), max(len(str(acc["summoner_name"])) for acc in accounts))
            tag_line_width = max(len("TAG"), max(len(str(acc["tag_line"])) for acc in accounts))
            region_width = max(len("REGION"), max(len(str(acc["region"])) for acc in accounts))
            sep = "  "
            total_width = id_width + summoner_width + tag_line_width + region_width + len(sep) * 3
            print(f"{'ID':<{id_width}}  {'SUMMONER':<{summoner_width}}  {'TAG':<{tag_line_width}}  {'REGION':<{region_width}}")
            print("-" * total_width)
            for acc in accounts:
                print(
                    f"{acc['id']:<{id_width}}  "
                    f"{acc['summoner_name']:<{summoner_width}}  "
                    f"{acc['tag_line']:<{tag_line_width}}  "
                    f"{acc['region']:<{region_width}}"
                    )       
    elif args.command == "summary":
        acc = storage.get_account(args.account_id)
        if not acc:
            print(f"Account not found <{args.account_id}>")
            exit(1)
        summ = riot_client.get_summoner_by_puuid(acc['region'], acc['puuid'], api_key)
        entries = riot_client.get_ranked_entries(acc["region"], acc["puuid"], api_key)
        soloq = None
        for entry in entries: 
            if entry["queueType"] == "RANKED_SOLO_5x5":
                soloq = entry
        print(f"Account #{acc['id']}: {acc['summoner_name']}#{acc['tag_line']} ({acc['region']})")
        print(f"Level: {summ['summonerLevel']}")
        if not soloq: 
            print("SoloQ: Unranked")
            return 0
        games = soloq["wins"] + soloq["losses"]
        wr = (soloq["wins"] / games) * 100
        print(f"SoloQ: {soloq['tier']} {soloq['rank']}-{soloq['leaguePoints']}LP ({soloq['wins']}W / {soloq['losses']}L) WR{wr:.1f}%")
        match_ids = riot_client.get_recent_match_ids(acc["puuid"], acc["region"], api_key)
        rows = []
        for i, match_id in enumerate(match_ids, start=1):
            match = riot_client.get_match(match_id, acc["region"], api_key)
            for player in match["info"]["participants"]:
                if player["puuid"] == acc["puuid"]:
                    result = "W" if player["win"] else "L"
                    rows.append({
                        "num": i,
                        "result": result,
                        "champ": player["championName"],
                        "k": player["kills"],
                        "d": player["deaths"],
                        "a": player["assists"],
                        "cs": player["totalMinionsKilled"] + player["neutralMinionsKilled"]
                    })

        if not rows:
            print("\nNo recent matches found.")
        else:
            num_w = max(len("#"), max(len(str(r["num"])) for r in rows))
            res_w = len("Result")
            champ_w = max(len("Champ"), max(len(r["champ"]) for r in rows))
            k_w = max(len("K"), max(len(str(r["k"])) for r in rows))
            d_w = max(len("D"), max(len(str(r["d"])) for r in rows))
            a_w = max(len("A"), max(len(str(r["a"])) for r in rows))
            cs_w = max(len("CS"), max(len(str(r["cs"])) for r in rows))

            total_width = num_w + res_w + champ_w + k_w + d_w + a_w + cs_w + 18

            print(f"\n{BOLD}Last 5 Matches{RESET}")
            print("-" * total_width)

            print(
                f"{'#':<{num_w}}  "
                f"{'Result':<{res_w}}  "
                f"{'Champ':<{champ_w}}  "
                f"{'K':>{k_w}}  "
                f"{'D':>{d_w}}  "
                f"{'A':>{a_w}}  "
                f"{'CS':>{cs_w}}"
            )

            print("-" * total_width)

            for r in rows:
                # Colorear resultado
                if r["result"] == "W":
                    result_colored = f"{GREEN}W{RESET}"
                else:
                    result_colored = f"{RED}L{RESET}"

                champ_colored = f"{CYAN}{r['champ']}{RESET}"

                print(
                    f"{r['num']:<{num_w}}  "
                    f"{result_colored:<{res_w + len(RESET) + len(GREEN)}}  "
                    f"{champ_colored:<{champ_w + len(RESET) + len(CYAN)}}  "
                    f"{r['k']:>{k_w}}  "
                    f"{r['d']:>{d_w}}  "
                    f"{r['a']:>{a_w}}  "
                    f"{r['cs']:>{cs_w}}"
                )
    elif args.command == "master-acc":
        accounts = storage.list_accounts()
        metrics_list = metrics.compute_all_accounts_metrics(accounts, api_key)
        master = metrics.compute_master_metrics(metrics_list)
        metrics.print_master_summary(master, metrics_list)
        
    else:
        parser.error("Unknown command")
    return 0