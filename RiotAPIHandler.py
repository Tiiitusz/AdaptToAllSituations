import requests

class RiotAPIHandler:
    def __init__(self, api_key, region):
        self.api_key = api_key
        self.region = region
        self.routing_region = self._resolve_routing_region(region)
        self.base_url = f"https://{self.routing_region}.api.riotgames.com"

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


    def getAccountByRiotID(self, gameName, tagLine):
        headers = {
            "X-Riot-Token": self.api_key
        }
        url = f"{self.base_url}/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            print(response.json())
            return response.json()
        except requests.exceptions.RequestException as exc:
            print(f"Request failed for URL: {url}")
            print(f"Error: {exc}")
            return None
