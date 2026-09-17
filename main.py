import flet as ft
import psutil
import wmi
import cupy as cp
import time
import asyncio
import os


def main(page: ft.Page):

    # =========================================================
    # CONFIGURAÇÃO DA PÁGINA
    # =========================================================

    page.title = "PC Analyzer"
    page.padding = 0
    page.bgcolor = "#111318"
    page.window.maximized = True

    # =========================================================
    # LIMITES DO DIAGNÓSTICO
    # =========================================================

    LIMITE_CPU = 85
    LIMITE_RAM = 85
    LIMITE_DISCO = 90

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
            problemas.append(
                "Armazenamento com pouco espaço livre."
            )

        if not problemas:
            return "✓ Nenhum problema importante identificado."

        return "⚠ " + " | ".join(problemas)

    # =========================================================
    # CONTEÚDO PRINCIPAL
    # =========================================================

    conteudo = ft.Container(
        expand=True,
        padding=30
    )

    # =========================================================
    # WMI
    # =========================================================

    try:
        computador = wmi.WMI()
    except Exception:
        computador = None

    # =========================================================
    # DESEMPENHO
    # =========================================================

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

    # =========================================================
    # HARDWARE
    # =========================================================

    processador = ft.Text(
        "--",
        color="#FFFFFF"
    )

    placa_mae = ft.Text(
        "--",
        color="#FFFFFF"
    )

    sistema = ft.Text(
        "--",
        color="#FFFFFF"
    )

    bios = ft.Text(
        "--",
        color="#FFFFFF"
    )

    gpu_wmi = ft.Text(
        "--",
        color="#FFFFFF"
    )

    # =========================================================
    # MEMÓRIA RAM
    # =========================================================

    ddr_memoria = ft.Text(
        "--",
        color="#FFFFFF"
    )

    frequencia_ram = ft.Text(
        "--",
        color="#FFFFFF"
    )

    capacidade_ram = ft.Text(
        "--",
        color="#FFFFFF"
    )

    # =========================================================
    # GPU
    # =========================================================

    gpu_nome = ft.Text(
        "--",
        color="#FFFFFF"
    )

    gpu_memoria = ft.Text(
        "--",
        color="#FFFFFF"
    )

    cuda = ft.Text(
        "--",
        color="#FFFFFF"
    )

    # =========================================================
    # DIAGNÓSTICO
    # =========================================================

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

    # =========================================================
    # BARRAS
    # =========================================================

    grafico_cpu = ft.ProgressBar(
        value=0,
        color="#00FF99",
        bgcolor="#2C313B"
    )

    grafico_ram = ft.ProgressBar(
        value=0,
        color="#2563EB",
        bgcolor="#2C313B"
    )

    grafico_disco = ft.ProgressBar(
        value=0,
        color="#F59E0B",
        bgcolor="#2C313B"
    )

    # =========================================================
    # INFORMAÇÕES DO COMPUTADOR
    # =========================================================

    if computador:

        # -----------------------------------------------------
        # PROCESSADOR
        # -----------------------------------------------------

        try:

            processadores = computador.Win32_Processor()

            if processadores:
                processador.value = (
                    processadores[0].Name.strip()
                )

        except Exception:
            pass

        # -----------------------------------------------------
        # PLACA-MÃE
        # -----------------------------------------------------

        try:

            placas = computador.Win32_BaseBoard()

            if placas:

                placa = placas[0]

                fabricante = placa.Manufacturer or ""
                modelo = placa.Product or ""

                placa_mae.value = (
                    f"{fabricante} {modelo}".strip()
                )

        except Exception:
            pass

        # -----------------------------------------------------
        # SISTEMA
        # -----------------------------------------------------

        try:

            sistemas = computador.Win32_OperatingSystem()

            if sistemas:

                sistema.value = (
                    sistemas[0].Caption
                )

        except Exception:
            pass

        # -----------------------------------------------------
        # BIOS
        # -----------------------------------------------------

        try:

            bios_info = computador.Win32_BIOS()

            if bios_info:

                bios.value = (
                    bios_info[0].SMBIOSBIOSVersion
                    or "--"
                )

        except Exception:
            pass

        # -----------------------------------------------------
        # GPU
        # -----------------------------------------------------

        try:

            placas_video = (
                computador.Win32_VideoController()
            )

            if placas_video:

                gpu_wmi.value = (
                    placas_video[0].Name
                    or "--"
                )

        except Exception:
            pass

    # =========================================================
    # MEMÓRIA RAM
    # =========================================================

    if computador:

        try:

            memorias = (
                computador.Win32_PhysicalMemory()
            )

            tipos_ddr = {
                20: "DDR",
                21: "DDR2",
                22: "DDR2 FB-DIMM",
                24: "DDR3",
                26: "DDR4",
                34: "DDR5"
            }

            # -------------------------------------------------
            # TIPO DDR
            # -------------------------------------------------

            tipo_memoria = None

            for memoria in memorias:

                tipo = tipos_ddr.get(
                    getattr(
                        memoria,
                        "SMBIOSMemoryType",
                        None
                    )
                )

                if tipo:

                    tipo_memoria = tipo
                    break

            if not tipo_memoria:

                for memoria in memorias:

                    tipo = tipos_ddr.get(
                        getattr(
                            memoria,
                            "MemoryType",
                            None
                        )
                    )

                    if tipo:

                        tipo_memoria = tipo
                        break

            if tipo_memoria:

                ddr_memoria.value = tipo_memoria

            else:

                ddr_memoria.value = (
                    "Não identificado"
                )

            # -------------------------------------------------
            # FREQUÊNCIA CONFIGURADA
            # -------------------------------------------------

            frequencia_atual = None

            for memoria in memorias:

                velocidade = getattr(
                    memoria,
                    "ConfiguredClockSpeed",
                    None
                )

                if velocidade:

                    frequencia_atual = int(
                        velocidade
                    )

                    break

            # -------------------------------------------------
            # FALLBACK
            # -------------------------------------------------

            if not frequencia_atual:

                for memoria in memorias:

                    velocidade = getattr(
                        memoria,
                        "Speed",
                        None
                    )

                    if velocidade:

                        frequencia_atual = int(
                            velocidade
                        )

                        break

            if frequencia_atual:

                frequencia_ram.value = (
                    f"{frequencia_atual} MHz"
                )

            else:

                frequencia_ram.value = (
                    "Não identificada"
                )

            # -------------------------------------------------
            # CAPACIDADE TOTAL
            # -------------------------------------------------

            total_ram = 0

            for memoria in memorias:

                capacidade = getattr(
                    memoria,
                    "Capacity",
                    None
                )

                if capacidade:

                    total_ram += (
                        int(capacidade)
                        / (1024 ** 3)
                    )

            if total_ram > 0:

                capacidade_ram.value = (
                    f"{total_ram:.0f} GB"
                )

            else:

                capacidade_ram.value = (
                    "Não identificada"
                )

        except Exception:

            ddr_memoria.value = (
                "Não identificado"
            )

            frequencia_ram.value = (
                "Não identificada"
            )

            capacidade_ram.value = (
                "Não identificada"
            )

    # =========================================================
    # GPU / CUDA
    # =========================================================

    try:

        dispositivo = cp.cuda.Device()

        propriedades = (
            cp.cuda.runtime.getDeviceProperties(
                dispositivo.id
            )
        )

        nome_gpu = propriedades["name"]

        if isinstance(nome_gpu, bytes):

            nome_gpu = nome_gpu.decode(
                errors="ignore"
            )

        gpu_nome.value = str(nome_gpu)

        memoria_gpu = (
            dispositivo.mem_info[1]
            / (1024 ** 3)
        )

        gpu_memoria.value = (
            f"{memoria_gpu:.2f} GB"
        )

        cuda.value = str(
            cp.cuda.runtime.runtimeGetVersion()
        )

    except Exception:

        gpu_nome.value = (
            "GPU/CUDA não disponível"
        )

        gpu_memoria.value = "--"
        cuda.value = "--"

    # =========================================================
    # REDE
    # =========================================================

    dados_rede = psutil.net_io_counters()

    download_anterior = (
        dados_rede.bytes_recv
    )

    upload_anterior = (
        dados_rede.bytes_sent
    )

    tempo_anterior = time.time()

    # =========================================================
    # ATUALIZAÇÃO
    # =========================================================

    def atualizar(e=None):

        nonlocal download_anterior
        nonlocal upload_anterior
        nonlocal tempo_anterior

        # CPU
        cpu_val = psutil.cpu_percent()

        # RAM
        ram_val = (
            psutil.virtual_memory().percent
        )

        # DISCO
        try:

            disco_val = psutil.disk_usage(
                os.path.abspath(os.sep)
            ).percent

        except Exception:

            disco_val = 0

        cpu.value = f"{cpu_val:.0f}%"
        ram.value = f"{ram_val:.0f}%"
        disco.value = f"{disco_val:.0f}%"

        # =====================================================
        # BARRAS
        # =====================================================

        grafico_cpu.value = cpu_val / 100
        grafico_ram.value = ram_val / 100
        grafico_disco.value = disco_val / 100

        # =====================================================
        # REDE
        # =====================================================

        rede = psutil.net_io_counters()

        tempo = (
            time.time()
            - tempo_anterior
        )

        velocidade_download = 0.0
        velocidade_upload = 0.0

        if tempo > 0:

            velocidade_download = (
                rede.bytes_recv
                - download_anterior
            ) / tempo / (1024 ** 2)

            velocidade_upload = (
                rede.bytes_sent
                - upload_anterior
            ) / tempo / (1024 ** 2)

        download.value = (
            f"{velocidade_download:.2f} MB/s"
        )

        upload.value = (
            f"{velocidade_upload:.2f} MB/s"
        )

        download_anterior = rede.bytes_recv
        upload_anterior = rede.bytes_sent
        tempo_anterior = time.time()

        # =====================================================
        # DIAGNÓSTICO
        # =====================================================

        diagnostico_texto.value = diagnosticar(
            cpu_val,
            ram_val,
            disco_val
        )

        maior = max(
            cpu_val,
            ram_val,
            disco_val
        )

        if maior >= 90:

            status_geral.value = "CRÍTICO"
            status_geral.color = "#FF4D4D"

        elif maior >= 75:

            status_geral.value = "ATENÇÃO"
            status_geral.color = "#F59E0B"

        else:

            status_geral.value = (
                "DESEMPENHO NORMAL"
            )

            status_geral.color = "#00FF99"

        page.update()

    # =========================================================
    # ATUALIZAÇÃO AUTOMÁTICA
    # =========================================================

    async def atualizar_automaticamente():

        while True:

            atualizar()

            await asyncio.sleep(2)

    # =========================================================
    # TELA DE DESEMPENHO
    # =========================================================

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

                ft.Row(

                    [

                        # CPU
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
                                                "Processador",
                                                color="#2563EB"
                                            ),

                                            ft.Icon(
                                                ft.Icons.MEMORY,
                                                color="#2563EB"
                                            )

                                        ],

                                        alignment=(
                                            ft.MainAxisAlignment
                                            .SPACE_BETWEEN
                                        )
                                    ),

                                    cpu

                                ]
                            )
                        ),

                        # RAM
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
                                                "Memória RAM",
                                                color="#2563EB"
                                            ),

                                            ft.Icon(
                                                ft.Icons.MEMORY,
                                                color="#2563EB"
                                            )

                                        ],

                                        alignment=(
                                            ft.MainAxisAlignment
                                            .SPACE_BETWEEN
                                        )
                                    ),

                                    ram

                                ]
                            )
                        ),

                        # DISCO
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
                                                "Armazenamento",
                                                color="#2563EB"
                                            ),

                                            ft.Icon(
                                                ft.Icons.STORAGE,
                                                color="#2563EB"
                                            )

                                        ],

                                        alignment=(
                                            ft.MainAxisAlignment
                                            .SPACE_BETWEEN
                                        )
                                    ),

                                    disco

                                ]
                            )
                        )

                    ]
                ),

                # =================================================
                # REDE
                # =================================================

                ft.Container(

                    padding=20,
                    bgcolor="#1A1D24",
                    border_radius=10,

                    content=ft.Column(

                        [

                            ft.Row(

                                [

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

                                alignment=(
                                    ft.MainAxisAlignment
                                    .SPACE_BETWEEN
                                )
                            ),

                            ft.Divider(
                                color="#2C313B"
                            ),

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

                        ]
                    )
                )
            ]
        )

    # =========================================================
    # TELA DE HARDWARE
    # =========================================================

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

                    content=ft.Column(

                        [

                            ft.Row(

                                [

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

                                alignment=(
                                    ft.MainAxisAlignment
                                    .SPACE_BETWEEN
                                )
                            ),

                            ft.Divider(
                                color="#2C313B"
                            ),

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

                            gpu_wmi,

                            ft.Divider(
                                color="#2C313B"
                            ),

                            ft.Text(
                                "Memória RAM",
                                size=18,
                                weight="bold",
                                color="#2563EB"
                            ),

                            ft.Text(
                                "Tipo",
                                color="#9CA3AF"
                            ),

                            ddr_memoria,

                            ft.Text(
                                "Frequência configurada",
                                color="#9CA3AF"
                            ),

                            frequencia_ram,

                            ft.Text(
                                "Capacidade total",
                                color="#9CA3AF"
                            ),

                            capacidade_ram

                        ],

                        spacing=10
                    )
                )
            ]
        )

    # =========================================================
    # TELA GPU
    # =========================================================

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

                    content=ft.Column(

                        [

                            ft.Row(

                                [

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

                                alignment=(
                                    ft.MainAxisAlignment
                                    .SPACE_BETWEEN
                                )
                            ),

                            ft.Divider(
                                color="#2C313B"
                            ),

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

                        ]
                    )
                )
            ]
        )

    # =========================================================
    # TELA DE DIAGNÓSTICO
    # =========================================================

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
                    "Análise automática do desempenho "
                    "do computador",
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

                            ft.Divider(
                                color="#2C313B"
                            ),

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

                            ft.Text(
                                "CPU",
                                color="#9CA3AF"
                            ),

                            grafico_cpu,

                            ft.Text(
                                "RAM",
                                color="#9CA3AF"
                            ),

                            grafico_ram,

                            ft.Text(
                                "Armazenamento",
                                color="#9CA3AF"
                            ),

                            grafico_disco

                        ],

                        spacing=8
                    )
                )
            ]
        )

    # =========================================================
    # TELAS
    # =========================================================

    telas = {
        "Desempenho": tela_desempenho(),
        "Hardware": tela_hardware(),
        "Placa de Vídeo": tela_gpu(),
        "Diagnóstico": tela_diagnostico()
    }

    # =========================================================
    # NAVEGAÇÃO
    # =========================================================

    def navegar(e):

        conteudo.content = telas[
            e.control.data
        ]

        page.update()

    # =========================================================
    # BOTÕES DO MENU
    # =========================================================

    def botao(nome, icone):

        return ft.Container(

            padding=15,
            border_radius=10,
            data=nome,
            on_click=navegar,

            content=ft.Row(

                [

                    ft.Icon(
                        icone,
                        size=22,
                        color="#2563EB"
                    ),

                    ft.Text(
                        nome,
                        color="#FFFFFF"
                    )

                ]
            )
        )

    # =========================================================
    # MENU LATERAL
    # =========================================================

    # IMPORTANTE:
    # Aqui NÃO usamos:
    #
    # ft.alignment.center
    # ft.Alignment(...)
    # ft.ImageFit
    #
    # A centralização é feita pela própria Column.

    logo = ft.Image(
        src="logo.jpg",
        width=100,
        height=100
    )

    nome_programa = ft.Text(
        "PC ANALYZER",
        size=22,
        weight="bold",
        color="#00FF99",
        text_align=ft.TextAlign.CENTER
    )

    subtitulo = ft.Text(
        "Monitoramento do computador",
        size=12,
        color="#9CA3AF",
        text_align=ft.TextAlign.CENTER
    )

    menu = ft.Container(

        width=230,

        bgcolor="#17191F",

        padding=20,

        content=ft.Column(

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                # =================================================
                # LOGO
                # =================================================

                ft.Container(
                    width=190,
                    height=125,
                    content=ft.Column(
                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                        alignment=(
                            ft.MainAxisAlignment.CENTER
                        ),
                        controls=[
                            logo
                        ]
                    )
                ),

                # =================================================
                # NOME
                # =================================================

                ft.Container(
                    width=190,
                    content=nome_programa
                ),

                # =================================================
                # SUBTÍTULO
                # =================================================

                ft.Container(
                    width=190,
                    content=subtitulo
                ),

                # =================================================
                # LINHA
                # =================================================

                ft.Divider(
                    color="#2C313B"
                ),

                # =================================================
                # MENU
                # =================================================

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
                )

            ]
        )
    )

    # =========================================================
    # ESTRUTURA PRINCIPAL
    # =========================================================

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

    # =========================================================
    # TELA INICIAL
    # =========================================================

    conteudo.content = telas[
        "Desempenho"
    ]

    # =========================================================
    # PRIMEIRA ATUALIZAÇÃO
    # =========================================================

    atualizar()

    # =========================================================
    # ATUALIZAÇÃO AUTOMÁTICA
    # =========================================================

    page.run_task(
        atualizar_automaticamente
    )


# =============================================================
# INICIAR PROGRAMA
# =============================================================

ft.run(
    main,
    assets_dir="Assets"
)