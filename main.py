import json
import flet as ft
import RiotAPIHandler


def main(page: ft.Page):
    page.title = "Example Riot API App"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24
    page.window_width = 500
    page.window_height = 500
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    colors = ft.Colors if hasattr(ft, "Colors") else ft.colors
    icons = ft.Icons if hasattr(ft, "Icons") else ft.icons

    api_key = ft.TextField(
        label="Riot API Key",
        password=True,
        can_reveal_password=True,
        autofocus=True,
    )

    region = ft.TextField(
        label="Region (e.g., EUNE, EUW, NA)",
        value="EUNE",
    )

    game_name = ft.TextField(
        label="Game Name (Riot ID)",
        value="TunaSub",
    )
    tag_line = ft.TextField(
        label="Tag Line (Riot ID)",
        value="EUNE",
    )

    output = ft.TextField(
        label="Response",
        multiline=True,
        min_lines = 10,
        max_lines = 20,
        read_only=True,
    )

    loading_ring = ft.ProgressRing(visible=False)

    def show_error(message: str):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), open=True)
        page.update()
    
    def fetch_account(_):
        if not api_key.value or not region.value or not game_name.value or not tag_line.value:
            show_error("Please fill in all fields.")
            return

        loading_ring.visible = True
        output.value = "Fetching account..."
        page.update()

        handler = RiotAPIHandler.RiotAPIHandler(api_key.value.strip(), region.value.strip())
        data = handler.getAccountByRiotID(game_name.value.strip(), tag_line.value.strip())

        loading_ring.visible = False
        if data is None:
            output.value = "Request failed. Check API key, Riot ID, and region."
        else:
            output.value = json.dumps(data, indent=2)
        page.update()

    page.add(
        ft.Container(
            width=780,
            padding=24,
            border_radius=18,
            bgcolor=colors.with_opacity(0.08, colors.BLUE_200),
            content=ft.Column(
                controls=[
                    ft.Text("Riot Account Lookup", size=30, weight=ft.FontWeight.W_700),
                    ft.Text(
                        "Modern desktop UI powered by Flet.",
                        size=14,
                        color=colors.BLUE_GREY_300,
                    ),
                    api_key,
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(content=region, col={"xs": 12, "md": 4}),
                            ft.Container(content=game_name, col={"xs": 12, "md": 4}),
                            ft.Container(content=tag_line, col={"xs": 12, "md": 4}),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Fetch Account",
                                icon=icons.SEARCH,
                                on_click=fetch_account,
                            ),
                            loading_ring,
                        ]
                    ),
                    output,
                ],
                spacing=14,
            ),
        )
    )

if __name__ == "__main__":
    ft.app(target=main)

