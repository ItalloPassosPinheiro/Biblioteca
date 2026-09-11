import flet as ft
import cupy as cp


def main(page: ft.Page):
    page.title = "PC Analyzer"
    page.padding = 0
    page.window.maximized = True

    conteudo = ft.Container(expand=True, padding=25)

    def titulo(nome, descricao):
        return ft.Column([
            ft.Text(nome, size=30, weight="bold", color="#FFFFFF")
        ])

    def card(nome, valor, unidade, icone, cor):
        return ft.Container(
            expand=True, padding=20, bgcolor="#1A1D24",
            border_radius=12, border=ft.Border.all(1, "#2C313B"),
            content=ft.Column([
                ft.Row([
                    ft.Text(nome, color="#9CA3AF"),
                    ft.Icon(icone, color=cor)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(valor, size=28, weight="bold", color="#FFFFFF"),
                    ft.Text(unidade, color="#9CA3AF")
                ]),
                ft.ProgressBar(value=.35, color=cor, bgcolor="#30343D")
            ])
        )

    def tela(nome, descricao, icone, cor, biblioteca):
        return ft.Column(
            expand=True, spacing=20,
            controls=[
                titulo(nome, descricao),

                ft.Row([
                    card("Utilização", "0", "%", icone, cor),
                    card("Temperatura", "--", "°C",
                         ft.Icons.THERMOSTAT, "#EF4444"),
                    card("Frequência", "--", "GHz",
                         ft.Icons.SPEED, "#3B82F6")
                ]),

                ft.Container(
                    expand=True, padding=25, bgcolor="#1A1D24",
                    border_radius=12,
                    border=ft.Border.all(1, "#2C313B"),
                    content=ft.Column([
                        ft.Text(
                            "Informações detalhadas",
                            size=20, weight="bold", color="#FFFFFF"
                        ),
                        ft.Divider(color="#2C313B"),
                        ft.Row([
                            ft.Icon(icone, size=55, color=cor),
                            ft.Text(
                                nome, size=22,
                                weight="bold", color="#FFFFFF"
                            )
                        ]),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column([
                                ft.Icon(ft.Icons.INSERT_CHART,size=60, color=cor
                                ),
                                ft.Text("ÁREA PARA GRÁFICOS",size=20,weight="bold",color="#FFFFFF")],horizontal_alignment=ft.CrossAxisAlignment.CENTER,alignment=ft.MainAxisAlignment.CENTER)
                        )
                    ])
                )
            ]
        )

    dashboard = ft.Column(
        expand=True, spacing=20,
        controls=[
            titulo("Dashboard", ""),

            ft.Row([
                card("CPU", "35", "%", ft.Icons.MEMORY, "#3B82F6"),
                card("RAM", "62", "%", ft.Icons.MEMORY, "#8B5CF6"),
                card("Disco", "28", "%", ft.Icons.STORAGE, "#F59E0B"),
                card("GPU", "41", "%",
                     ft.Icons.VIDEOGAME_ASSET, "#22C55E")
            ]),

            ft.Row(
                expand=True,
                controls=[
                    ft.Container(
                        expand=2, bgcolor="#1A1D24", padding=25,
                        border_radius=12,
                        content=ft.Column([
                            ft.Text(
                                "Monitoramento de desempenho",
                                size=18, weight="bold", color="#FFFFFF"
                            ),
                            ft.Divider(color="#2C313B"),
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Column([
                                    ft.Icon(
                                        ft.Icons.SHOW_CHART,
                                        size=60, color="#3B82F6"
                                    ),
                                    ft.Text(
                                        "GRÁFICO",
                                        size=20,
                                        weight="bold",
                                        color="#FFFFFF"
                                    ),
                                    ft.Text(
                                        "Área preparada para dados em tempo real",
                                        color="#9CA3AF"
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER)
                            )
                        ])
                    ),

                    ft.Container(
                        expand=1, bgcolor="#1A1D24", padding=25,
                        border_radius=12,
                        content=ft.Column([
                            ft.Text(
                                "Status do sistema",
                                size=18, weight="bold", color="#FFFFFF"
                            ),
                            ft.Divider(color="#2C313B"),
                            ft.Text("● CPU     Normal", color="#22C55E"),
                            ft.Text("● RAM     Normal", color="#22C55E"),
                            ft.Text("● GPU     Normal", color="#22C55E"),
                            ft.Text("● Disco   Normal", color="#22C55E")
                        ])
                    )
                ]
            )
        ]
    )

    telas = {
        "Dashboard": dashboard,

        "Processador": tela(
            "Processador", "", ft.Icons.MEMORY,
            "#3B82F6", "Psutil + WMI"
        ),

        "GPU": tela(
            "GPU", "", ft.Icons.VIDEOGAME_ASSET,
            "#22C55E", "WMI + CuPy"
        ),

        "Memória": tela(
            "Memória RAM", "", ft.Icons.MEMORY,
            "#8B5CF6", "Psutil + WMI"
        ),

        "Armazenamento": tela(
            "Armazenamento", "", ft.Icons.STORAGE,
            "#F59E0B", "Psutil + WMI"
        ),

        "Rede": tela(
            "Rede", "", ft.Icons.NETWORK_CHECK,
            "#3B82F6", "Psutil"
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
        width=220, bgcolor="#17191F", padding=20,
        content=ft.Column([
            ft.Text(
                "PC ANALYZER",
                size=22, weight="bold", color="#FFFFFF"
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

