import flet as ft
import psutil
import wmi
import cupy as cp
import time
import asyncio


def main(page: ft.Page):

    page.title = "PC Analyzer"
    page.padding = 0
    page.window.maximized = True
    page.bgcolor = "#111318"

    conteudo = ft.Container(
        expand=True,
        padding=30
    )

    computador = wmi.WMI()

    cpu = ft.Text(
        "0%",
        size=28,
        weight="bold",
        color="#FFFFFF"
    )

    ram = ft.Text(
        "0%",
        size=28,
        weight="bold",
        color="#FFFFFF"
    )

    disco = ft.Text(
        "0%",
        size=28,
        weight="bold",
        color="#FFFFFF"
    )

    download = ft.Text(
        "0 MB/s",
        size=28,
        weight="bold",
        color="#FFFFFF"
    )

    upload = ft.Text(
        "0 MB/s",
        size=28,
        weight="bold",
        color="#FFFFFF"
    )

    processador = ft.Text("--", color="#FFFFFF")
    placa_mae = ft.Text("--", color="#FFFFFF")
    sistema = ft.Text("--", color="#FFFFFF")
    bios = ft.Text("--", color="#FFFFFF")
    gpu_wmi = ft.Text("--", color="#FFFFFF")

    gpu_nome = ft.Text("--", color="#FFFFFF")
    gpu_memoria = ft.Text("--", color="#FFFFFF")
    cuda = ft.Text("--", color="#FFFFFF")

    try:

        processador.value = computador.Win32_Processor()[0].Name.strip()

        placa_mae.value = (
            computador.Win32_BaseBoard()[0].Manufacturer
            + " "
            + computador.Win32_BaseBoard()[0].Product
        )

        sistema.value = computador.Win32_OperatingSystem()[0].Caption

        bios.value = computador.Win32_BIOS()[0].SMBIOSBIOSVersion

        gpu_wmi.value = computador.Win32_VideoController()[0].Name

    except Exception:
        pass

    try:

        dispositivo = cp.cuda.Device()

        gpu_nome.value = cp.cuda.runtime.getDeviceProperties(
            dispositivo.id
        )["name"].decode()

        memoria = dispositivo.mem_info[1] / (1024 ** 3)

        gpu_memoria.value = f"{memoria:.2f} GB"

        cuda.value = cp.cuda.runtime.runtimeGetVersion()

    except Exception:

        gpu_nome.value = "GPU/CUDA não disponível"
        gpu_memoria.value = "--"
        cuda.value = "--"

    dados_rede = psutil.net_io_counters()

    download_anterior = dados_rede.bytes_recv
    upload_anterior = dados_rede.bytes_sent
    tempo_anterior = time.time()

    def atualizar(e=None):

        nonlocal download_anterior
        nonlocal upload_anterior
        nonlocal tempo_anterior

        cpu.value = f"{psutil.cpu_percent()}%"
        ram.value = f"{psutil.virtual_memory().percent}%"
        disco.value = f"{psutil.disk_usage('/').percent}%"

        rede = psutil.net_io_counters()

        tempo = time.time() - tempo_anterior

        if tempo > 0:

            velocidade_download = (
                rede.bytes_recv - download_anterior
            ) / tempo / (1024 ** 2)

            velocidade_upload = (
                rede.bytes_sent - upload_anterior
            ) / tempo / (1024 ** 2)

            download.value = f"{velocidade_download:.2f} MB/s"
            upload.value = f"{velocidade_upload:.2f} MB/s"

        download_anterior = rede.bytes_recv
        upload_anterior = rede.bytes_sent
        tempo_anterior = time.time()

        page.update()

    async def atualizar_automaticamente():

        while True:
            atualizar()
            await asyncio.sleep(2)

    # ==========================================================
    # DESEMPENHO
    # ==========================================================

    def tela_desempenho():

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[

                ft.Text(
                    "Desempenho",
                    size=30,
                    weight="bold",
                    color="#00FF99"
                ),

                ft.Text(
                    "Monitoramento em tempo real",
                    color="#9CA3AF"
                ),

                ft.Row([

                    ft.Container(
                        expand=True,
                        padding=20,
                        bgcolor="#1A1D24",
                        border_radius=10,
                        content=ft.Column([

                            ft.Row([
                                ft.Text(
                                    "Processador",
                                    color="#2563EB"
                                ),

                                ft.Icon(
                                    ft.Icons.MEMORY,
                                    color="#2563EB"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                            cpu

                        ])
                    ),

                    ft.Container(
                        expand=True,
                        padding=20,
                        bgcolor="#1A1D24",
                        border_radius=10,
                        content=ft.Column([

                            ft.Row([
                                ft.Text(
                                    "Memória RAM",
                                    color="#2563EB"
                                ),

                                ft.Icon(
                                    ft.Icons.MEMORY,
                                    color="#2563EB"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                            ram

                        ])
                    ),

                    ft.Container(
                        expand=True,
                        padding=20,
                        bgcolor="#1A1D24",
                        border_radius=10,
                        content=ft.Column([

                            ft.Row([
                                ft.Text(
                                    "Armazenamento",
                                    color="#2563EB"
                                ),

                                ft.Icon(
                                    ft.Icons.STORAGE,
                                    color="#2563EB"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                            disco

                        ])
                    )

                ]),

                ft.Container(
                    padding=20,
                    bgcolor="#1A1D24",
                    border_radius=10,

                    content=ft.Column([

                        ft.Row([
                            ft.Text(
                                "Rede",
                                size=20,
                                weight="bold",
                                color="#2563EB"
                            ),

                            ft.Icon(
                                ft.Icons.NETWORK_CHECK,
                                color="#2563EB"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Divider(color="#2C313B"),

                        ft.Text(
                            "Download",
                            color="#9CA3AF"
                        ),

                        download,

                        ft.Text(
                            "Upload",
                            color="#9CA3AF"
                        ),

                        upload

                    ])
                )
            ]
        )

    # ==========================================================
    # HARDWARE
    # ==========================================================

    def tela_hardware():

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[

                ft.Text(
                    "Hardware",
                    size=30,
                    weight="bold",
                    color="#00FF99"
                ),

                ft.Text(
                    "Informações do computador",
                    color="#9CA3AF"
                ),

                ft.Container(
                    expand=True,
                    padding=25,
                    bgcolor="#1A1D24",
                    border_radius=10,

                    content=ft.Column([

                        ft.Row([
                            ft.Text(
                                "Componentes",
                                size=20,
                                weight="bold",
                                color="#2563EB"
                            ),

                            ft.Icon(
                                ft.Icons.COMPUTER,
                                color="#2563EB"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Divider(color="#2C313B"),

                        ft.Text(
                            "Processador",
                            color="#9CA3AF"
                        ),

                        processador,

                        ft.Text(
                            "Placa-mãe",
                            color="#9CA3AF"
                        ),

                        placa_mae,

                        ft.Text(
                            "Sistema operacional",
                            color="#9CA3AF"
                        ),

                        sistema,

                        ft.Text(
                            "BIOS",
                            color="#9CA3AF"
                        ),

                        bios,

                        ft.Text(
                            "Placa de vídeo",
                            color="#9CA3AF"
                        ),

                        gpu_wmi

                    ])
                )
            ]
        )

    # ==========================================================
    # PLACA DE VÍDEO
    # ==========================================================

    def tela_gpu():

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[

                ft.Text(
                    "Placa de Vídeo",
                    size=30,
                    weight="bold",
                    color="#00FF99"
                ),

                ft.Text(
                    "Informações e recursos gráficos",
                    color="#9CA3AF"
                ),

                ft.Container(
                    expand=True,
                    padding=25,
                    bgcolor="#1A1D24",
                    border_radius=10,

                    content=ft.Column([

                        ft.Row([
                            ft.Text(
                                "Informações da GPU",
                                size=20,
                                weight="bold",
                                color="#2563EB"
                            ),

                            ft.Icon(
                                ft.Icons.VIDEOGAME_ASSET,
                                color="#2563EB"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Divider(color="#2C313B"),

                        ft.Text(
                            "GPU",
                            color="#9CA3AF"
                        ),

                        gpu_nome,

                        ft.Text(
                            "Memória",
                            color="#9CA3AF"
                        ),

                        gpu_memoria,

                        ft.Text(
                            "CUDA",
                            color="#9CA3AF"
                        ),

                        cuda

                    ])
                )
            ]
        )

    telas = {

        "Desempenho": tela_desempenho(),

        "Hardware": tela_hardware(),

        "Placa de Vídeo": tela_gpu()

    }

    def navegar(e):

        conteudo.content = telas[e.control.data]

        page.update()

    def botao(nome, icone):

        return ft.Container(
            padding=15,
            border_radius=10,
            data=nome,
            on_click=navegar,

            content=ft.Row([

                ft.Icon(
                    icone,
                    size=22,
                    color="#2563EB"
                ),

                ft.Text(
                    nome,
                    color="#FFFFFF"
                )

            ])
        )

    menu = ft.Container(
        width=230,
        bgcolor="#17191F",
        padding=20,

        content=ft.Column([

            ft.Text(
                "PC ANALYZER",
                size=22,
                weight="bold",
                color="#00FF99"
            ),

            ft.Text(
                "Monitoramento do computador",
                size=12,
                color="#9CA3AF"
            ),

            ft.Divider(color="#2C313B"),

            botao(
                "Desempenho",
                ft.Icons.SPEED
            ),

            botao(
                "Hardware",
                ft.Icons.COMPUTER
            ),

            botao(
                "Placa de Vídeo",
                ft.Icons.VIDEOGAME_ASSET
            )

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

    conteudo.content = telas["Desempenho"]

    atualizar()

    page.run_task(atualizar_automaticamente)


ft.app(target=main)
