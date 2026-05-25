import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class RiotAPIHandler:
    def __init__(self, api_key, region, game_name="", tag_line=""):
        self.api_key = api_key
        self.region = region
        self.game_name = game_name
        self.tag_line = tag_line
        self.routing_region = self._resolve_routing_region(region)
        self.platform = self._resolve_platform(region)
        self.base_url = f"https://{self.routing_region}.api.riotgames.com"
        self.platform_url = f"https://{self.platform}.api.riotgames.com"
        self.ATAS_challengeID = 602002
        self.puuid = None
        self.startMatch = 0
        self.min_request_interval = 0.01
        self.max_retries = 5
        self.lastRequestTs = 0.0

    def spaceRequests(self):
        elapsed = time.monotonic() - self.lastRequestTs
        if elapsed < self.min_request_interval:
            print("Slowing requests to avoid hitting rate limits for time " + str(self.min_request_interval - elapsed) + " seconds.")
            time.sleep(self.min_request_interval - elapsed)
        self.lastRequestTs = time.monotonic()

    def URLRequest(self, url):
        print(f"Requesting URL: {url}")
        headers = {
            "X-Riot-Token": self.api_key
        }

        for attempt in range(self.max_retries + 1):
            self.spaceRequests()

            try:
                response = requests.get(url, headers=headers, timeout=15)
            except requests.exceptions.RequestException as exc:
                print(f"Request exception for URL: {url}")
                if attempt == self.max_retries:
                    print(f"Request failed for URL: {url}")
                    print(f"Error: {exc}")
                    return None
                time.sleep(self.min_request_interval * (attempt + 1))
                continue

            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", "1"))
                time.sleep(max(retry_after, self.min_request_interval))
                continue

            try:
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as exc:
                if attempt == self.max_retries:
                    print(f"Request failed for URL: {url}")
                    print(f"Error: {exc}")
                    return None
                time.sleep(self.min_request_interval * (attempt + 1))

        print(f"Request failed for URL: {url}")
        print("Error: max retries exceeded")
        return None

    def _resolve_routing_region(self, region):
        normalized = region.strip().upper()

        # Account-V1 uses regional routing values, not platform shards.
        if normalized in {"AMERICAS", "EUROPE", "ASIA", "SEA"}:
            return normalized.lower()

        platform_to_routing = {
            "NA": "americas", "NA1": "americas",
            "BR": "americas", "BR1": "americas",
            "LAN": "americas", "LA1": "americas",
            "LAS": "americas", "LA2": "americas",
            "OCE": "americas", "OC1": "americas",
            "EUNE": "europe", "EUN1": "europe",
            "EUW": "europe", "EUW1": "europe",
            "TR": "europe", "TR1": "europe",
            "RU": "europe", "RU1": "europe",
            "KR": "asia", "KR1": "asia",
            "JP": "asia", "JP1": "asia",
            "PH": "sea", "PH2": "sea",
            "SG": "sea", "SG2": "sea",
            "TH": "sea", "TH2": "sea",
            "TW": "sea", "TW2": "sea",
            "VN": "sea", "VN2": "sea",
        }

        return platform_to_routing.get(normalized, normalized.lower())

    def _resolve_platform(self, region):
        normalized = region.strip().upper()
        region_to_platform = {
            "NA": "na1", "NA1": "na1",
            "BR": "br1", "BR1": "br1",
            "LAN": "la1", "LA1": "la1",
            "LAS": "la2", "LA2": "la2",
            "OCE": "oc1", "OC1": "oc1",
            "EUNE": "eun1", "EUN1": "eun1",
            "EUW": "euw1", "EUW1": "euw1",
            "TR": "tr1", "TR1": "tr1",
            "RU": "ru", "RU1": "ru",
            "KR": "kr", "KR1": "kr",
            "JP": "jp1", "JP1": "jp1",
            "PH": "ph2", "PH2": "ph2",
            "SG": "sg2", "SG2": "sg2",
            "TH": "th2", "TH2": "th2",
            "TW": "tw2", "TW2": "tw2",
            "VN": "vn2", "VN2": "vn2",
        }
        return region_to_platform.get(normalized, normalized.lower())

    def getPUUID(self):
        if self.puuid == None:
            data = self.getAccountByRiotID()
            self.puuid = data.get("puuid")
        return self.puuid

    def getAccountByRiotID(self):
        url = f"{self.base_url}/riot/account/v1/accounts/by-riot-id/{self.game_name}/{self.tag_line}"
        data = self.URLRequest(url)
        if data is not None:
            self.puuid = data.get("puuid")
        return data

    def getATASProgress(self):
        data = self.getAccountByRiotID()
        if data is None:
            return None

        puuid = data.get("puuid")
        url = f"{self.platform_url}/lol/challenges/v1/player-data/{puuid}"
        data = self.URLRequest(url)
        if data is None:
            return None

        for challange in data.get("challenges", []):
            if challange["challengeId"] == self.ATAS_challengeID:
                return challange["value"]
        return 0
        
    def getMatches(self, count=20):
        puuid = self.getPUUID()
        if puuid is None:
            return []

        url = f"{self.base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={self.startMatch}&count={count}"

        data = self.URLRequest(url)
        # treat empty list (no IDs) the same as None: no more history available
        if not data:
            return []

        # only advance the start offset when we successfully received IDs
        self.startMatch += count

        def fetch_match(matchId):
            url = f"{self.base_url}/lol/match/v5/matches/{matchId}"
            matchData = self.URLRequest(url)
            if matchData is None:
                return None
            if matchData["info"]["gameMode"] != "CHERRY":
                return None
            for participant in matchData["info"]["participants"]:
                if participant["puuid"] == puuid:
                    return participant
            return None

        arenaGames = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_match, matchId): matchId for matchId in data}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    arenaGames.append(result)
        return arenaGames
        