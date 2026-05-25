import json
import flet as ft
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

    def init_ui(self):
        self.api_key = ft.TextField(
            label="Riot API Key",
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
                                    on_click=self.fetch_account,
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

    def fetch_account(self, _):
        if not self.api_key.value or not self.region.value or not self.game_name.value or not self.tag_line.value:
            self.show_error("Please fill in all fields.")
            return
        
        self.loading_ring.visible = True
        self.output.value = "Fetching account..."
        self.page.update()

        handler = RiotAPIHandler.RiotAPIHandler(self.api_key.value.strip(), self.region.value.strip())
        data = handler.getAccountByRiotID(self.game_name.value.strip(), self.tag_line.value.strip())

        self.loading_ring.visible = False
        if data is None:
            self.output.value = "Request failed. Check API key, Riot ID, and region."
        else:
            self.output.value = json.dumps(data, indent=2)
        self.page.update()

    

if __name__ == "__main__":
    ft.app(target=main)

