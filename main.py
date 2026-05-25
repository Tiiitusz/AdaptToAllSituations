import json
import time
import flet as ft
import os

import RiotAPIHandler

class main():
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Example Riot API App"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 24
        self.page.window_width = 500
        self.page.window_height = 500
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.colors = ft.Colors if hasattr(ft, "Colors") else ft.colors
        self.icons = ft.Icons if hasattr(ft, "Icons") else ft.icons

        self.init_ui()
        self.build()

        self.champsWon = []

    def init_ui(self):
        self.api_key = ft.TextField(
            label="Riot API Key",
            value="RGAPI-8fc73704-7017-4c6c-8167-77468679a1b1",
            password=True,
            can_reveal_password=True,
            autofocus=True,
        )

        self.region = ft.TextField(
            label="Region (e.g., EUNE, EUW, NA)",
            value="EUNE",
        )

        self.game_name = ft.TextField(
            label="Game Name (Riot ID)",
            value="TunaSub",
        )

        self.tag_line = ft.TextField(
            label="Tag Line (Riot ID)",
            value="EUNE",
        )

        self.output = ft.TextField(
            label="Response",
            multiline=True,
            min_lines=10,
            max_lines=20,
            read_only=True,
        )

        self.loading_ring = ft.ProgressRing(visible=False)

    def build(self):
        self.page.add(
            ft.Container(
                width=780,
                padding=24,
                border_radius=18,
                bgcolor=self.colors.with_opacity(0.08, self.colors.BLUE_200),
                content=ft.Column(
                    controls=[
                        ft.Text("Riot Account Lookup", size=30, weight=ft.FontWeight.W_700),
                        ft.Text(
                            "Modern desktop UI powered by Flet.",
                            size=14,
                            color=self.colors.BLUE_GREY_300,
                        ),
                        self.api_key,
                        ft.ResponsiveRow(
                            controls=[
                                ft.Container(content=self.region, col={"xs": 12, "md": 4}),
                                ft.Container(content=self.game_name, col={"xs": 12, "md": 4}),
                                ft.Container(content=self.tag_line, col={"xs": 12, "md": 4}),
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Fetch Account",
                                    icon=self.icons.SEARCH,
                                    on_click=self.initAPIHandler,
                                ),
                                self.loading_ring,
                            ]
                        ),
                        self.output,
                    ],
                    spacing=14,
                ),
            )
        )
    
    def show_error(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.update()

    def initChampsWon(self):
        self.champsWon = []
        if os.path.exists(f"data/{self.APIHandler.getPUUID()}.json"):
            with open(f"data/{self.APIHandler.getPUUID()}.json", "r") as f:
                self.champsWon = json.load(f)
        else:
            with open(f"data/{self.APIHandler.getPUUID()}.json", "w") as f:
                json.dump(self.champsWon, f)

    def initAPIHandler(self, _):
        if not self.api_key.value or not self.region.value or not self.game_name.value or not self.tag_line.value:
            self.show_error("Please fill in API key, region, game name, and tag line.")
            return None
        
        self.APIHandler = RiotAPIHandler.RiotAPIHandler(self.api_key.value.strip(), self.region.value.strip(), self.game_name.value.strip(), self.tag_line.value.strip())
        self.getAccountInfo()
    
    def fetch_account(self):
        self.loading_ring.visible = True
        self.setOutput("Fetching account...")
        data = self.APIHandler.getAccountByRiotID()
        self.loading_ring.visible = False
        self.setOutput(data)

    def fetch_atasProgress(self):
        self.loading_ring.visible = True
        self.setOutput("Fetching ATAS progress...")
        numberOfWins = self.APIHandler.getATASProgress()
        self.loading_ring.visible = False
        self.setOutput(numberOfWins)

    def getWonChamps(self, noWins):
        file = open(f"data/{self.APIHandler.getPUUID()}.json", "w")
        stringbuilder = ""
        while len(self.champsWon) < noWins:
            ams = self.APIHandler.getMatches(20)
            for am in ams:
                if am["PlayerScore0"] == 1 and am["championName"] not in self.champsWon:
                    file = open(f"data/{self.APIHandler.getPUUID()}.json", "w") 
                    self.champsWon.append(am["championName"])
                    json.dump(self.champsWon, file)
                    file.close()
                    stringbuilder = f"Found win with {am['championName']}!\n" + stringbuilder
                    self.setOutput(f"Total wins found: {len(self.champsWon)} out of {noWins} \n" + stringbuilder)
            

    def getAccountInfo(self):
        self.loading_ring.visible = True
        self.setOutput("Fetching account wins...")
        noWins = self.APIHandler.getATASProgress()
        self.initChampsWon()
        print(self.champsWon)
        self.setOutput(f"Number of wins: {noWins}, fetching match history...")
        self.getWonChamps(noWins)
        self.loading_ring.visible = False
        self.setOutput(f"Fetched {len(self.champsWon)} champions.")


    def setOutput(self, data):
        if data is None:
            self.output.value = "Request failed. Check API key, Riot ID, and region."
        else:
            if isinstance(data, str):
                # preserve user-provided newlines in plain strings
                self.output.value = data
            else:
                try:
                    self.output.value = json.dumps(data, indent=2)
                except Exception:
                    self.output.value = str(data)
        self.page.update()

if __name__ == "__main__":
    ft.app(target=main)

