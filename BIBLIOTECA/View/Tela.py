import flet as ft
import cupy as cp


def main(page: ft.Page):

    page.title = "PC Analyzer"
    page.padding = 0
    page.window.maximized = True
    page.bgcolor = "#111318"

    conteudo = ft.Container(expand=True, padding=25)

    def titulo(nome, descricao):
        return ft.Text(
            nome,
            size=28,
            weight="bold",
            color="#FFFFFF"
        )

    def card(nome, valor, icone, cor):
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor="#1A1D24",
            border_radius=10,
            content=ft.Column([
                ft.Row([
                    ft.Text(nome, color="#9CA3AF"),
                    ft.Icon(icone, color=cor)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                valor
            ])
        )

    def tela(nome, icone, cor):

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                titulo(nome, ""),

                ft.Row([
                    card(
                        "Utilização",
                        ft.Text("0%", size=28, weight="bold", color="#FFFFFF"),
                        icone,
                        cor
                    ),

                    card(
                        "Temperatura",
                        ft.Text("-- °C", size=28, weight="bold", color="#FFFFFF"),
                        ft.Icons.THERMOSTAT,
                        "#EF4444"
                    ),

                    card(
                        "Frequência",
                        ft.Text("-- GHz", size=28, weight="bold", color="#FFFFFF"),
                        ft.Icons.SPEED,
                        "#3B82F6"
                    )
                ]),

                ft.Container(
                    expand=True,
                    padding=20,
                    bgcolor="#1A1D24",
                    border_radius=10,
                    content=ft.Column([
                        ft.Text(
                            "Informações",
                            size=20,
                            weight="bold",
                            color="#FFFFFF"
                        ),

                        ft.Divider(color="#2C313B"),

                        ft.Text(
                            "Dados do componente aparecerão aqui.",
                            color="#9CA3AF"
                        )
                    ])
                )
            ]
        )

    dashboard = ft.Column(
        expand=True,
        spacing=20,
        controls=[

            titulo("Dashboard", ""),

            ft.Row([
                card(
                    "CPU",
                    ft.Text("0%", size=28, weight="bold", color="#FFFFFF"),
                    ft.Icons.MEMORY,
                    "#3B82F6"
                ),

                card(
                    "RAM",
                    ft.Text("0%", size=28, weight="bold", color="#FFFFFF"),
                    ft.Icons.MEMORY,
                    "#8B5CF6"
                ),

                card(
                    "Disco",
                    ft.Text("0%", size=28, weight="bold", color="#FFFFFF"),
                    ft.Icons.STORAGE,
                    "#F59E0B"
                ),

                card(
                    "GPU",
                    ft.Text("0%", size=28, weight="bold", color="#FFFFFF"),
                    ft.Icons.VIDEOGAME_ASSET,
                    "#22C55E"
                )
            ]),

            ft.Container(
                expand=True,
                padding=20,
                bgcolor="#1A1D24",
                border_radius=10,
                content=ft.Column([
                    ft.Text(
                        "Status do computador",
                        size=20,
                        weight="bold",
                        color="#FFFFFF"
                    ),

                    ft.Divider(color="#2C313B"),

                    ft.Text("CPU: Normal", color="#22C55E"),
                    ft.Text("RAM: Normal", color="#22C55E"),
                    ft.Text("GPU: Normal", color="#22C55E"),
                    ft.Text("Disco: Normal", color="#22C55E")
                ])
            )
        ]
    )

    telas = {
        "Dashboard": dashboard,

        "Processador": tela(
            "Processador",
            ft.Icons.MEMORY,
            "#3B82F6"
        ),

        "GPU": tela(
            "GPU",
            ft.Icons.VIDEOGAME_ASSET,
            "#22C55E"
        ),

        "Memória": tela(
            "Memória RAM",
            ft.Icons.MEMORY,
            "#8B5CF6"
        ),

        "Armazenamento": tela(
            "Armazenamento",
            ft.Icons.STORAGE,
            "#F59E0B"
        ),

        "Rede": tela(
            "Rede",
            ft.Icons.NETWORK_CHECK,
            "#3B82F6"
        )
    }

    def navegar(e):
        conteudo.content = telas[e.control.data]
        page.update()

    def botao(nome, icone):
        return ft.Container(
            padding=12,
            border_radius=8,
            data=nome,
            on_click=navegar,
            content=ft.Row([
                ft.Icon(icone, color="#9CA3AF"),
                ft.Text(nome, color="#9CA3AF")
            ])
        )

    menu = ft.Container(
        width=200,
        bgcolor="#17191F",
        padding=20,
        content=ft.Column([

            ft.Text(
                "PC ANALYZER",
                size=20,
                weight="bold",
                color="#FFFFFF"
            ),

            ft.Divider(color="#2C313B"),

            botao("Dashboard", ft.Icons.DASHBOARD),
            botao("Processador", ft.Icons.MEMORY),
            botao("GPU", ft.Icons.VIDEOGAME_ASSET),
            botao("Memória", ft.Icons.MEMORY),
            botao("Armazenamento", ft.Icons.STORAGE),
            botao("Rede", ft.Icons.NETWORK_CHECK),

            ft.Container(expand=True)
        ])
    )

    page.add(
        ft.Row(
            expand=True,
            spacing=0,
            controls=[
                menu,

                ft.Container(
                    expand=True,
                    bgcolor="#111318",
                    content=conteudo
                )
            ]
        )
    )

    conteudo.content = telas["Dashboard"]


ft.app(target=main)
