import requests
from lol_api_idf import get_champion_by_key
from datetime import datetime, timedelta
import concurrent.futures
import json
import os

# with open('config.json', 'r') as file:
#     config = json.load(file)
# api_key = config.get('RIOT_API')

with open('data/config.json', 'r') as file:
    config = json.load(file)

api_key = config.get('RIOT_API')

# TODO Make it so I can grab more matches 
# After make it so that everyone is atleast able to have an SR
# Accurancy right now is close to around 75% which is fine
# Im not happy with the tuner yet I waant to make it a bit closer, maybe calculating average dragon/baron
# And average cs woulld be nice

DATA_FILE = 'data/data.json'
DATA_EXPIRY_HOURS = 48

def load_data():
    """Load cached data from file"""
    if not os.path.exists(DATA_FILE):
        return {"players": {}, "last_updated": {}}
    
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"players": {}, "last_updated": {}}
    
def save_data(data):
    """Save data to cache file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_player_data(puuid):
    """Get player data from cache if recent enough"""
    data = load_data()
    player_data = data["players"].get(puuid)
    last_updated = data["last_updated"].get(puuid)
    
    if player_data and last_updated:
        last_update_time = datetime.fromisoformat(last_updated)
        if datetime.now() - last_update_time < timedelta(hours=DATA_EXPIRY_HOURS):
            return player_data
    return None

def update_player_data(puuid, player_data):
    """Update cache with new player data"""
    data = load_data()
    data["players"][puuid] = player_data
    data["last_updated"][puuid] = datetime.now().isoformat()
    save_data(data)






#getting account name and tagline by puuid

def getAccountTag(puuid: str, region: str = "americas"): #grabs account name and tag by puuid
    api_url = "https://{}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{}?api_key={}".format(region,puuid,api_key)

    try:

        response = requests.get(api_url)
        player_info = response.json()
        return "{}#{}".format(player_info['gameName'],player_info['tagLine'])

    except requests.exceptions.RequestException as e:
        return("Error getting account tag!")

def getPuuid(name: str, tag: str, region: str = "americas"): # gets the puuid from a riot tag uses new regions (ex: americas)
    api_url = "https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}".format(region,name,tag,api_key)

    try:
        response = requests.get(api_url)
        account_info = response.json()
        #print (account_info)
        return account_info['puuid']
    
    except requests.exceptions.RequestException as e:
        return("Error getting puuid!")


#print (getPuuid("GodBlonde","5499","americas"))
#print (getPuuid("Morememes","NA1","americas"))
#print (getPuuid("The Driver","robot"))

#get summoner

def getSummoner(puuid: str, region: str = "na1"): #grabs summoner data WARNING USES OLDER REGION TAGS
    """Get basic summoner profile data by PUUID.
    
    ⚠️ Uses older region tags (v4 API)
    
    Args:
        puuid: Player's unique ID
        region: Server region code (default: "na1")
    
    Returns:
        dict: Summoner data (id, name, level, etc.)
        str: Error message if API call fails
    """
    
    api_url = "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{}?api_key={}".format(region,puuid,api_key)

    try:
        response = requests.get(api_url)
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return("Error getting summoner!")


#print (getSummoner("odrM1Qv3RXmjHC_-EDuAVYUSfFFkbrzcbdRiqtYHhmKXWDrHTo4RHxfS9jU_jN92t6cDJolu3g6PGA")['id'])
#print (getSummoner("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA")['id'])
#print (getSummoner("tWIXuVh_yeQbixe2DVg-8nvAf7IkwEH_NriaT2G-kX7Rt0AjUhskd1NsBtv1hl_ExBCL2K0pnIYb1w")['id'])

#get rank

def getStats(id: str, region: str = "na1"): #get account game stats BY ID NOT PUUID
    """Get ranked stats for a summoner by ID.
    
    Args:
        id: Summoner ID (not PUUID)
        region: Server region code (default: "na1")
    
    Returns:
        dict: Ranked stats with tier/rank/LP if ranked
              Default UNRANKED dict if unranked
        str: Error message if API call fails
    Example Response:
        leagueId: 3a342298-b1a0-4ab3-966c-5972c807a01f
        queueType: RANKED_SOLO_5x5
        tier: "SILVER"
        rank: "II"
        summonerId: "FJ_3CABngRZ_7nBggFR3zAIp7lrMZVnY3DItxS1LtytQpKMa"
        summonerName: "Morememes"
        leaguePoints: 37
        wins: 13
        losses: 13
        veteran: false
        inactive: false
        freshBlood: false
        hotStreak: false
    """
    
    api_url = "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(region,id,api_key)

    try:
        response = requests.get(api_url)
        response = response.json()

        if response:
            return response[0]        
        else:
            response = {
                "tier": "UNRANKED",
                "rank": "",
                "wins": 0,
                "losses": 0,
                "leaguePoints": 0 
            }
            return response
    
    
    except requests.exceptions.RequestException as e:
        return("Error getting game stats!")
#print (getStats(getSummoner(getPuuid("The Driver","robot"))['id']))
#print (getStats("bZEzyw9zHqgtk3LWkmEs7d0Zqf7ioC3Qk5n1Pxu76gPKgM6W","na1"))
#print (getStats("kJd6IFeOBTZ8j-tuRAv3Ny1dpFm-dMTiB6Z_zi_WPLpCn4iQvb-agxESTg"))

#mastery handling 

def getMastery(puuid: str, count: int = 1): #returns mastery for champ(s) in count
    """Get top champion mastery data for a player.
    
    Args:
        puuid: Player's unique ID
        count: Number of top champions to return (default: 1)
    
    Returns:
        list: Champion names ordered by mastery (highest first)
        str: Error message if API call fails
    """
    
    api_url = "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{}/top?api_key={}&count={}".format(puuid,api_key,count)

    try:

        response = requests.get(api_url) 
        response.raise_for_status() e
        mastery_info = response.json()

        champion_names = []
        for mastery in mastery_info:
            champion_id = mastery['championId']
            champion_name = get_champion_by_key(champion_id, "en_US")['name']
            champion_names.append(champion_name)

        return champion_names
       

    except requests.exceptions.RequestException as e:
        return("Error getting mastery!")

# print (getMastery("mBTJkW5vuRHVSd2KmutqtpTv9-vU7tkVcEmxba7iwImElgbx5z6mbGn8DbA9HN9WZ0ob7cZWhbBBwg", 2)) #debug
    



def getMatch(id: str, region = "na1"):
    """Get real-time information about the summoner's current match.
    
    Fetches live game data from Riot's Spectator API for the specified summoner.

    Args:
        id (str): The summoner ID to look up current match for
        region (str, optional): The server region code. Defaults to "na1".
            Available regions: na1, euw1, eun1, etc.
    """
    api_url = "https://{}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{}?api_key={}".format(region, id, api_key)

    try:
        response = requests.get(api_url)
        return response
    except requests.exceptions.RequestException as e:
        return ("Error getting match!")
    
#print (getSummoner(getPuuid("Morememes","na1"))['id'])
#print (getMatch(getSummoner(getPuuid("Morememes","na1"))))
    

def extract_player_roles(match_details: str):
    if match_details is None:
        return None
    roles = {}
    if "info" in match_details and "participants" in match_details["info"]:
        for participant in match_details["info"]["participants"]:
            # Use puuid as key if summonerName is empty
            summoner_name = getAccountTag(participant["puuid"])
            puuid = participant["puuid"]
            role = participant["individualPosition"]
            roles[summoner_name] = {"role": role, "puuid": puuid}
    return roles


#my puuid zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA
#test match NA1_491158594
    
def getMatches(puuid: str, count: str, region: str = "americas"):
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api_key}"

    try:
        response = requests.get(api_url)
        match_list = response.json()

        filtered_match_list = []

        # Function to fetch match details and filter out non-ranked matches
        def fetch_match(match_id):
            match_details_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
            match_response = requests.get(match_details_url)
            match_data = match_response.json()
            game_mode = match_data.get('info', {}).get('gameMode')
            if game_mode == 'CLASSIC' or game_mode == 'RANKED':
                return match_id
            else:
                return None

        # Fetch match details concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_match, match_id) for match_id in match_list]
            concurrent.futures.wait(futures)

            # Collect filtered match IDs
            for future in futures:
                match_id = future.result()
                if match_id:
                    filtered_match_list.append(match_id)

        return filtered_match_list

    except requests.exceptions.RequestException as e:
        print(f"Error getting matches: {e}")
        print (match_list)
        return []


#print (getMatches("5oSjsiaQUOJr3wvbx2qkcX0u-C_yiOVKtCR4dRopJFzvutB9XEqf6p0Vq2VRC6VsLJQrqWoCW32N0g","1")) 
#print (getMatches(getPuuid("katevolved","666","americas"),"1"))
#print (getPuuid("Morememes","NA1"))
#print (getMatches(getPuuid("juvin","mae"),"5"))
#print (getMatches("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA","10","americas"))
    

def getmatchDetails(match_id: str, region: str = "americas"):
    api_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format(region, match_id, api_key)

    try:
        response = requests.get(api_url)
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return ("Error getting match!")


#print (getmatchDetails("NA1_5258439296"))
#print (extract_player_roles(getmatchDetails("NA1_4917316469")))


#getting invalid match data because if within the count provided no ranked or normal games are played
#it will not return the match data
#if only have played aram or urf it will return an error

def getmatchStats(puuid: str, region: str = "americas", ids: list = None):
    if ids is None:
        ids = getMatches(puuid, 5, region)[:1]

    total_tower_damage = 0
    total_deaths = 0
    total_kills = 0
    total_assists = 0
    total_cs = 0

    try:
        def fetch_match_data(match_id):
            try:
                api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
                response = requests.get(api_url)
                match_data = response.json()

                meta_data = match_data['metadata']
                index = meta_data['participants'].index(puuid)
                player_data = match_data['info']['participants'][index]

                return {
                    "towerDamage": player_data['damageDealtToTurrets'],
                    "deaths": player_data['deaths'],
                    "kills": player_data['kills'],
                    "assists": player_data['assists'],
                    "cs": player_data['neutralMinionsKilled'] + player_data['totalMinionsKilled']
                }
            except Exception as e:
                print(f"Error fetching match {match_id}: {e}")
                return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            match_data_list = list(executor.map(fetch_match_data, ids))

        num_matches = len(match_data_list)
        for match_data in match_data_list:
            if match_data:
                total_tower_damage += match_data['towerDamage']
                total_deaths += match_data['deaths']
                total_kills += match_data['kills']
                total_assists += match_data['assists']
                total_cs += match_data['cs']

        if num_matches > 0:
            average_data = {
                "towerDamage": int(total_tower_damage / num_matches),
                "deaths": int(total_deaths / num_matches),
                "kills": int(total_kills / num_matches),
                "assists": int(total_assists / num_matches),
                "cs": int(total_cs / num_matches)
            }
            return average_data
        else:
            average_data = {
                "towerDamage": 0,
                "deaths": 0,
                "kills": 0,
                "assists": 0,
                "cs": 0
            }
            print ("No valid match data")
            return average_data

    except requests.exceptions.RequestException as e:
        average_data = {
                "towerDamage": 0,
                "deaths": 0,
                "kills": 0,
                "assists": 0,
                "cs": 0
            }
        print (f"Error getting match: {e}")
        print (match_data)
        return average_data




#print (getmatchStats("5oSjsiaQUOJr3wvbx2qkcX0u-C_yiOVKtCR4dRopJFzvutB9XEqf6p0Vq2VRC6VsLJQrqWoCW32N0g","americas"))

#SUMMONER RATING CALCULATION

#roman numeral converter really shitty but funny
def rnC(input: str = None):
    if input is not None:
        con = input
        con = con.replace("IV","1")
        con = con.replace("III","2")
        con = con.replace("II","3")
        con = con.replace("I","4")
        return int(con)
    else:
        return 0

#adds a bonus to being a higher rank, however if they are unranked this bonus is ignored
def tierScore(tier: str = None):
    tier_scores = {
        "CHALLENGER": 32,
        "GRANDMASTER": 24,
        "MASTER": 20,
        "DIAMOND": 14,
        "EMERALD": 10,
        "PLATINUM": 7,
        "GOLD": 4,
        "SILVER": 3,
        "BRONZE": 2,
        "IRON": 1
    }
    return tier_scores.get(tier, 0) 

#applying a bonus for lp in the apex tiers
def lpBonus(tier: str):
    lp_bonus = {
        "CHALLENGER": 2.5,
        "GRANDMASTER": 2,
        "MASTER": 1,
    }
    return lp_bonus.get(tier, 0)

#find what basic champion roles counter the other
#will probally need more looking into maybe even subclasses
#and possibly role they champion is being played in
def counterCalc(role1: str, role2: str):
    counters = {
        "tank": ["fighter", "marksman"],
        "controller": ["fighter", "slayer"],
        "slayer": ["tank"],
        "mage": ["slayer", "tank"],
        "marksman": ["mage"],
        "fighter": ["marksman"]

    }


#main calculation for SR
def calcSR(puuid: str = None):
    print ("calc sr {}".format(puuid))
    cached_data = get_player_data(puuid)
    if cached_data:
        try:
            print("found cached data!")
            return int(cached_data.get("cached_sr", 0))
        except:
            pass
    try:
        stats = getmatchStats(puuid, "americas")
        #print (stats)
        id = getSummoner(puuid)['id']
        rank_stats = getStats(id, "na1")
        tier = rank_stats['tier']
        #print ("pass1")
        # if tier == "UNRANKED":
        #     return 0

        LP = rank_stats['leaguePoints']
        #print ("pass2")
        wins = rank_stats['wins']
        #print ("pass3")
        losses = rank_stats['losses']
        #print ("pass4")
        rank = rank_stats['rank']
        #print ("pass5")
        average_kills = stats['kills']
        #print ("pass6")
        average_deaths = stats['deaths']
        #print ("pass7")
        average_assists = stats['assists']
        #print ("pass8")
        average_tower_damage = stats['towerDamage']
        #print ("pass9")
        average_cs = stats['cs']
        #print ("pass10")
        #print(f"{average_tower_damage} / 175 | {average_kills} / {average_deaths} | {average_assists} / {average_deaths} | ")

        if tier in {"MASTER", "GRANDMASTER", "CHALLENGER"}:
            rank = LP * 0.05 * lpBonus(tier)
        if tier == "UNRANKED":
            rank = 1
        else:
            rank = rnC(rank)


#all of these can be changed to make certain stats more important or not
        tower_damage_bonus = average_tower_damage / 175
        KD = average_kills / average_deaths
        KDA_rating = ((KD / 1) * 10) + ((average_assists / average_deaths) * 2)
        CS_bonus = average_cs / 50
        
        if tierScore(tier) > 0:
            rank_bonus = (tierScore(tier) + (rank * 0.2)) * 5
        else:
            rank_bonus = 0
        SR = int(rank_bonus + tower_damage_bonus + KDA_rating + CS_bonus )
        if SR is None:
            SR = 0
        cache_entry = {
            "cached_sr": SR,
            "tier": tier,
            "rank": rank,
            "kda": KDA_rating,
            "wins": wins,
            "losses": losses,
            "last_updated": datetime.now().isoformat()
        }
        update_player_data(puuid, cache_entry)
        return SR
    except Exception as e:
        print(f"Error calculating SR: {e}")
        return 0


#print (calcSR("5oSjsiaQUOJr3wvbx2qkcX0u-C_yiOVKtCR4dRopJFzvutB9XEqf6p0Vq2VRC6VsLJQrqWoCW32N0g"))

#this is prob just gonna be wrong but who care rn

def calcPercent(SR1: int, SR2: int) -> dict:
    """Enhanced win prediction with role-based adjustments"""
    BLUE_SIDE_ADVANTAGE = 1.05  # 5% advantage
    
    effective_SR1 = SR1 * BLUE_SIDE_ADVANTAGE
    total = effective_SR1 + SR2
    
    chance = (effective_SR1 / total) * 100
    chance = max(10, min(90, chance))  # Keep between 10-90%
    
    return {
        "winner": "Blue Side" if effective_SR1 > SR2 else "Red Side",
        "chance": round(chance, 1),
        "confidence": get_confidence_level(abs(50 - chance))
    }

def get_confidence_level(difference: float) -> str:
    if difference > 20: return "High"
    if difference > 10: return "Medium"
    return "Low"




#print (calcPercent(62.84571428571428*5,112.84571428571428+62.462*4))
#print (calcSR(getPuuid("The Driver","robot")))

#print (calcSR(getPuuid("Morememes","NA1")))





#print (getmatchDetails("NA1_4920877607"))
#print (extract_player_roles(getmatchDetails("NA1_5258439296")))


# Main problem looks like rate limit is begin exceded
# to get around this I will try to break the prediction into two parts then add

# #main error when predicting matches
# Error fetching match NA1_4917730925: 'metadata'
# Error fetching match NA1_4917771608: 'metadata'
# Error fetching match NA1_4917812460: 'metadata'
# Error calculating SR: division by zero
# calc sr Te5q6seXlnuFr-anG56Vsc9FQyAUQRC47vM-ZAJ2ezhm8MZNzFJIGLdXOLHh2OZUhQlDthQVFjhgbw
# Error calculating SR: string indices must be integers, not 'str'
# calc sr LMbyUUjiNndegs4_8decr8PyZJOk5pOLMPBteWR5L_at7esDdlRNxCIYC6V54WacuQu4Oc558yNJKA
# Error calculating SR: string indices must be integers, not 'str'
# calc sr Jwoy5n9iD0ETsKGbojK4nbMys6xbnlvXAOhTStHfvmzI2TNxynFeIBgu_9oe5yI3RHfhgE2SFH8n_g
# Error calculating SR: string indices must be integers, not 'str'
# calc sr Jc5EvvhGeOd3M7YIeljqxvwq8OhwvZQiv-KlOcWKYSFo-hAyzopnzxysmdpkB12c8iF3nNYRCZhL0Q
# Error calculating SR: string indices must be integers, not 'str'