import json
import time
import flet as ft
import os
from pathlib import Path

import RiotAPIHandler

class main():
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Adapt to All Situations"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 24
        self.page.window_width = 1100
        self.page.window_height = 600
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.colors = ft.Colors if hasattr(ft, "Colors") else ft.colors
        self.icons = ft.Icons if hasattr(ft, "Icons") else ft.icons
        self.champsWon = []

        self.init_ui()
        self.build()
        
        
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
        # Buttons: keep fetch and manage disabled until API handler is initialized
        self.login_button = ft.ElevatedButton(
            "Log In",
            icon=self.icons.LOGIN,
            on_click=self.initAPIHandler,
        )

        self.fetch_button = ft.ElevatedButton(
            "Fetch Account",
            icon=self.icons.SEARCH,
            on_click=self.getAccountInfo,
            disabled=True,
        )
        # Champion sidebar
        with open("data/champions.json", "r") as f:
            try:
                self.champs = json.load(f)
            except Exception:
                self.champs = []

        self.champ_list = ft.Column(scroll=True, spacing=8, expand=True)
        self._rebuild_champ_list()

    def build(self):
        # left: main card; right: champion scroll list
        left_card = ft.Container(
            width=800,
            height=600,
            padding=24,
            border_radius=18,
            bgcolor=self.colors.with_opacity(0.08, self.colors.BLUE_200),
            content=ft.Column(
                controls=[
                    ft.Text("Adapt to All Situations tracker", size=30, weight=ft.FontWeight.W_700),
                    ft.Text(
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
                            self.login_button,
                            self.fetch_button,
                            self.loading_ring,
                        ]
                    ),
                    self.output,
                ],
                spacing=14,
            ),
        )

        print(self.champ_list)

        # limit champion list height to the page height so it becomes scrollable
        list_container = ft.Container(content=self.champ_list, height=500, expand=False)

        # create as instance attribute so we can toggle visibility later
        self.right_card = ft.Container(
            bgcolor=self.colors.with_opacity(0.04, self.colors.BLUE_200),
            width=300,
            height=600,
            padding=12,
            border_radius=12,
            visible=False,
            content=ft.Column([
                ft.Text("Champions", weight=ft.FontWeight.W_600),
                ft.Divider(),
                list_container,
            ], spacing=8),
        )


        # replace any existing controls with the new layout
        self.page.controls.clear()
        self.page.add(
            ft.Row(
                controls=[
                    left_card,
                    self.right_card
                ]
            )
        )
        self.page.update()
    
    def show_error(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), open=True)
        self.page.update()

    def _rebuild_champ_list(self):
        if not hasattr(self, 'champs') or self.champ_list is None:
            return
        self.champ_list.controls.clear()
        for champ in self.champs:
            if champ in self.champsWon:
                img_path = f"champion_icons_won/{champ}.png"
            else:
                img_path = f"champion_icons/{champ}.png"
            img = ft.Image(src=img_path, width=75, height=75)
            img_gesture = ft.GestureDetector(content=img, on_tap=lambda e, name=champ: self.onChampionClick(name))
            label = ft.Text(champ, size=12)
            row = ft.Row([img_gesture, ft.Container(width=8), label], alignment=ft.MainAxisAlignment.START)
            self.champ_list.controls.append(row)
        self.page.update()

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

    def initChampsWon(self):
        self.champsWon = []
        if os.path.exists(f"data/{self.APIHandler.getPUUID()}.json"):
            with open(f"data/{self.APIHandler.getPUUID()}.json", "r") as f:
                try:
                    self.champsWon = json.load(f)
                except json.JSONDecodeError:
                    self.champsWon = []
        else:
            with open(f"data/{self.APIHandler.getPUUID()}.json", "w") as f:
                json.dump(self.champsWon, f)
        self._rebuild_champ_list()


    def onChampionClick(self, name: str):
        if name in self.champsWon:
            self.champsWon.remove(name)
            self.setOutput(f"Removed {name} from wins. Tracked wins: {len(self.champsWon)}")
            file = open(f"data/{self.APIHandler.getPUUID()}.json", "w")
            json.dump(self.champsWon, file)
            file.close()
        else:
            self.champsWon.append(name)
            self.setOutput(f"Added {name} to wins. Tracked wins: {len(self.champsWon)}")
            file = open(f"data/{self.APIHandler.getPUUID()}.json", "w")
            json.dump(self.champsWon, file)
            file.close()
        self._rebuild_champ_list()

    def initAPIHandler(self, _):
        if not self.api_key.value or not self.region.value or not self.game_name.value or not self.tag_line.value:
            self.show_error("Please fill in API key, region, game name, and tag line.")
            return None
        
        self.loading_ring.visible = True
        self.setOutput("Checking API key and account info...")
        try:
            self.APIHandler = RiotAPIHandler.RiotAPIHandler(self.api_key.value.strip(), self.region.value.strip(), self.game_name.value.strip(), self.tag_line.value.strip())
        except Exception as e:
            print(e)
            self.loading_ring.visible = False
            self.fetch_button.disabled = True
            self.right_card.visible = False
            self.setOutput(f"Error initializing API key or account info")
            return
        
        self.initChampsWon()
        print(self.champsWon)
        self.loading_ring.visible = False
        self.fetch_button.disabled = False
        self.right_card.visible = True

        self.setOutput("Key and account info valid. You can now fetch account info and wins.")
        
    def getAccountInfo(self, _):
        self.loading_ring.visible = True
        self.setOutput("Fetching account wins...")
        noWins = self.APIHandler.getATASProgress()
        self.setOutput(f"Number of wins: {noWins}, fetching match history...")
        self.getWonChamps(noWins)
        self.loading_ring.visible = False
        self.setOutput(f"Finished fetching match history. Found {len(self.champsWon)} wins out of {noWins}.")
        

    def getWonChamps(self, noWins):
        stringbuilder = ""
        while len(self.champsWon) < noWins:
            start = self.APIHandler.getStartMatch()
            if start > 879:
                self.setOutput(f"Reached end of match history. Found {len(self.champsWon)} wins out of {noWins}.")
                return
            ams = self.APIHandler.getMatches(20)
            if not ams:
                self.setOutput(f"Reached end of match history. Found {len(self.champsWon)} wins out of {noWins}.")
                return
            self.setOutput(f"Fetched {start + 20} matches. \nTotal wins found: {len(self.champsWon)} out of {noWins} \n" + stringbuilder)
            for am in ams:
                if am["PlayerScore0"] == 1 and am["championName"] not in self.champsWon:
                    file = open(f"data/{self.APIHandler.getPUUID()}.json", "w") 
                    self.champsWon.append(am["championName"])
                    self._rebuild_champ_list()
                    json.dump(self.champsWon, file)
                    file.close()
                    stringbuilder = f"Found win with {am['championName']}!\n" + stringbuilder
                    self.setOutput(f"Fetched {start + 20} matches. \nTotal wins found: {len(self.champsWon)} out of {noWins} \n" + stringbuilder)
            


if __name__ == "__main__":
    ft.app(target=main)

