# from .main import ChatVox
import flet as ft


def main(page: ft.Page):
    page.title = "ChatVox"

    top_view = ft.View(
        "/",
        [
            ft.AppBar(
                title=ft.Text("ChatVox"),
                bgcolor=ft.colors.SURFACE_VARIANT,
                actions=[
                    ft.IconButton(
                        ft.icons.SETTINGS, on_click=lambda _: page.go("/settings")
                    )
                ],
            ),
            ft.Row([ft.Text("わんコメを起動"), ft.ElevatedButton("起動", "START")]),
            ft.Row(
                [
                    ft.Text("Style Bert VITSを起動"),
                    ft.ElevatedButton("起動", "START"),
                ]
            ),
        ],
    )

    settings_view = ft.View(
        "/settings",
        [
            ft.AppBar(
                title=ft.Text("ChatVox"),
                bgcolor=ft.colors.SURFACE_VARIANT,
            ),
            ft.Row(
                [
                    ft.Text("スピーカー"),
                    ft.Dropdown(
                        options=[ft.dropdown.Option(i) for i in ["A", "B", "C"]]
                    ),
                ]
            ),
        ],
    )

    def route_change(route):
        page.views.clear()
        page.views.append(top_view)
        if page.route == "/settings":
            page.views.append(settings_view)
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")


if __name__ == "__main__":
    ft.app(target=main)
