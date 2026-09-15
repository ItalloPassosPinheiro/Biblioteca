import flet as ft
import psutil
import wmi
import cupy as cp
import time
import asyncio
from collections import deque
from datetime import datetime
import sqlite3
import os


def main(page: ft.Page):

    page.title = "PC Analyzer"
    page.padding = 0
    page.window.maximized = True
    page.bgcolor = "#111318"

    # ==========================================================
    # CONFIGURAÇÕES DA ANÁLISE
    # ==========================================================

    BANCO = "historico_desempenho.db"
    LIMITE_CPU = 85
    LIMITE_RAM = 85
    LIMITE_DISCO = 90

    historico_cpu = deque(maxlen=30)
    historico_ram = deque(maxlen=30)
    historico_disco = deque(maxlen=30)

    def preparar_banco():
        with sqlite3.connect(BANCO) as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS desempenho (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    cpu REAL NOT NULL,
                    ram REAL NOT NULL,
                    disco REAL NOT NULL,
                    download REAL NOT NULL,
                    upload REAL NOT NULL
                )
            """)
            conexao.commit()

    preparar_banco()

    def salvar_historico(cpu_val, ram_val, disco_val, download_val, upload_val):
        with sqlite3.connect(BANCO) as conexao:
            conexao.execute(
                """
                INSERT INTO desempenho
                (data_hora, cpu, ram, disco, download, upload)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    cpu_val, ram_val, disco_val, download_val, upload_val
                )
            )
            conexao.commit()

    def nivel_desempenho(valor):
        if valor >= 90:
            return "CRÍTICO"
        if valor >= 75:
            return "ALTO"
        if valor >= 50:
            return "MODERADO"
        return "NORMAL"

    def diagnosticar(cpu_val, ram_val, disco_val):
        problemas = []

        if cpu_val >= 90:
            problemas.append("CPU em nível crítico.")
        elif cpu_val >= LIMITE_CPU:
            problemas.append("CPU com utilização elevada.")

        if ram_val >= 90:
            problemas.append("RAM em nível crítico.")
        elif ram_val >= LIMITE_RAM:
            problemas.append("RAM com utilização elevada.")

        if disco_val >= 95:
            problemas.append("Armazenamento quase cheio.")
        elif disco_val >= LIMITE_DISCO:
            problemas.append("Armazenamento com pouco espaço livre.")

        if not problemas:
            return "✓ Nenhum problema importante identificado."

        return "⚠ " + " | ".join(problemas)


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

    status_geral = ft.Text(
        "Analisando...",
        size=20,
        weight="bold",
        color="#00FF99"
    )

    diagnostico_texto = ft.Text(
        "Aguardando dados...",
        color="#FFFFFF",
        size=15
    )

    processo_lista = ft.Column(
        spacing=8,
        scroll=ft.ScrollMode.AUTO
    )

    grafico_cpu = ft.ProgressBar(value=0, color="#00FF99", bgcolor="#2C313B")
    grafico_ram = ft.ProgressBar(value=0, color="#2563EB", bgcolor="#2C313B")
    grafico_disco = ft.ProgressBar(value=0, color="#F59E0B", bgcolor="#2C313B")


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

        cpu_val = psutil.cpu_percent()
        ram_val = psutil.virtual_memory().percent
        disco_val = psutil.disk_usage(os.path.abspath(os.sep)).percent

        cpu.value = f"{cpu_val:.0f}%"
        ram.value = f"{ram_val:.0f}%"
        disco.value = f"{disco_val:.0f}%"

        grafico_cpu.value = cpu_val / 100
        grafico_ram.value = ram_val / 100
        grafico_disco.value = disco_val / 100

        historico_cpu.append(cpu_val)
        historico_ram.append(ram_val)
        historico_disco.append(disco_val)

        rede = psutil.net_io_counters()
        tempo = time.time() - tempo_anterior

        velocidade_download = 0.0
        velocidade_upload = 0.0

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

        diagnostico_texto.value = diagnosticar(
            cpu_val, ram_val, disco_val
        )

        maior = max(cpu_val, ram_val, disco_val)
        if maior >= 90:
            status_geral.value = "CRÍTICO"
            status_geral.color = "#FF4D4D"
        elif maior >= 75:
            status_geral.value = "ATENÇÃO"
            status_geral.color = "#F59E0B"
        else:
            status_geral.value = "DESEMPENHO NORMAL"
            status_geral.color = "#00FF99"

        salvar_historico(
            cpu_val, ram_val, disco_val,
            velocidade_download, velocidade_upload
        )

        # Processos que mais consomem CPU.
        processos = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                info = proc.info
                processos.append((
                    info["cpu_percent"] or 0,
                    info["memory_percent"] or 0,
                    info["name"] or "Desconhecido",
                    info["pid"]
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processos.sort(reverse=True, key=lambda x: x[0])

        processo_lista.controls.clear()

        for cpu_proc, ram_proc, nome, pid in processos[:6]:
            processo_lista.controls.append(
                ft.Container(
                    padding=10,
                    bgcolor="#111318",
                    border_radius=8,
                    content=ft.Row(
                        [
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            nome,
                                            color="#FFFFFF",
                                            weight="bold"
                                        ),
                                        ft.Text(
                                            f"PID: {pid}",
                                            color="#9CA3AF",
                                            size=11
                                        )
                                    ],
                                    spacing=2
                                )
                            ),
                            ft.Text(
                                f"CPU {cpu_proc:.1f}%",
                                color="#00FF99"
                            ),
                            ft.Text(
                                f"RAM {ram_proc:.1f}%",
                                color="#2563EB"
                            )
                        ]
                    )
                )
            )

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

    # ==========================================================
    # DIAGNÓSTICO
    # ==========================================================

    def tela_diagnostico():
        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                ft.Text(
                    "Diagnóstico",
                    size=30,
                    weight="bold",
                    color="#00FF99"
                ),
                ft.Text(
                    "Análise automática do desempenho do computador",
                    color="#9CA3AF"
                ),
                ft.Container(
                    padding=25,
                    bgcolor="#1A1D24",
                    border_radius=10,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Status atual",
                                size=20,
                                weight="bold",
                                color="#2563EB"
                            ),
                            status_geral,
                            ft.Divider(color="#2C313B"),
                            diagnostico_texto
                        ],
                        spacing=15
                    )
                ),
                ft.Container(
                    padding=20,
                    bgcolor="#1A1D24",
                    border_radius=10,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Níveis de utilização",
                                size=20,
                                weight="bold",
                                color="#2563EB"
                            ),
                            ft.Text("CPU", color="#9CA3AF"),
                            grafico_cpu,
                            ft.Text("RAM", color="#9CA3AF"),
                            grafico_ram,
                            ft.Text("Armazenamento", color="#9CA3AF"),
                            grafico_disco
                        ],
                        spacing=8
                    )
                )
            ]
        )

    # ==========================================================
    # PROCESSOS
    # ==========================================================

    def tela_processos():
        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                ft.Text(
                    "Processos",
                    size=30,
                    weight="bold",
                    color="#00FF99"
                ),
                ft.Text(
                    "Aplicações que mais utilizam os recursos do computador",
                    color="#9CA3AF"
                ),
                ft.Container(
                    expand=True,
                    padding=20,
                    bgcolor="#1A1D24",
                    border_radius=10,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        "Processo",
                                        size=20,
                                        weight="bold",
                                        color="#2563EB"
                                    ),
                                    ft.Icon(
                                        ft.Icons.TASK,
                                        color="#2563EB"
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(color="#2C313B"),
                            processo_lista
                        ]
                    )
                )
            ]
        )

    # ==========================================================
    # HISTÓRICO
    # ==========================================================

    def tela_historico():
        registros = []

        try:
            with sqlite3.connect(BANCO) as conexao:
                registros = conexao.execute(
                    """
                    SELECT data_hora, cpu, ram, disco
                    FROM desempenho
                    ORDER BY id DESC
                    LIMIT 20
                    """
                ).fetchall()
        except Exception:
            pass

        linhas = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(data, color="#FFFFFF")),
                    ft.DataCell(ft.Text(f"{c:.0f}%", color="#FFFFFF")),
                    ft.DataCell(ft.Text(f"{r:.0f}%", color="#FFFFFF")),
                    ft.DataCell(ft.Text(f"{d:.0f}%", color="#FFFFFF"))
                ]
            )
            for data, c, r, d in registros
        ]

        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data", color="#9CA3AF")),
                ft.DataColumn(ft.Text("CPU", color="#9CA3AF")),
                ft.DataColumn(ft.Text("RAM", color="#9CA3AF")),
                ft.DataColumn(ft.Text("Disco", color="#9CA3AF"))
            ],
            rows=linhas
        )

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                ft.Text(
                    "Histórico",
                    size=30,
                    weight="bold",
                    color="#00FF99"
                ),
                ft.Text(
                    "Últimas medições registradas",
                    color="#9CA3AF"
                ),
                ft.Container(
                    expand=True,
                    padding=20,
                    bgcolor="#1A1D24",
                    border_radius=10,
                    content=ft.Column(
                        [tabela],
                        scroll=ft.ScrollMode.AUTO
                    )
                )
            ]
        )

    telas = {

        "Desempenho": tela_desempenho(),

        "Hardware": tela_hardware(),

        "Placa de Vídeo": tela_gpu(),
        "Diagnóstico": tela_diagnostico(),
        "Processos": tela_processos(),
        "Histórico": tela_historico()

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
            ),

            botao(
                "Diagnóstico",
                ft.Icons.HEALTH_AND_SAFETY
            ),

            botao(
                "Processos",
                ft.Icons.TASK
            ),

            botao(
                "Histórico",
                ft.Icons.HISTORY
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