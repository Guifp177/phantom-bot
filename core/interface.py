"""
Interface Manager - PHANTOM BOT
UI Premium com Rich: ASCII animado, background, seletor de contas
"""
import time
import itertools
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.columns import Columns
from rich import box
from rich.style import Style

# ─── NOME DO BOT ────────────────────────────────────────────────────────────────

BOT_NAME = "PHANTOM"

PHANTOM_ASCII = r"""
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
"""

# Fundo decorativo ASCII que preenche a tela
BG_TILE = "░▒▓"

# Cores que o ASCII vai ciclar
ASCII_COLOR_CYCLE = itertools.cycle([
    "bright_magenta",
    "bright_cyan",
    "bright_blue",
    "cyan",
    "magenta",
    "bright_white",
])

MENU_OPTIONS = {
    "1": ("📦  Criar Contas (até 10, paralelo)", "bright_green"),
    "2": ("👁️   Auto-View  ─  Vídeo / Stories",  "cyan"),
    "3": ("❤️   Auto-Like  ─  Curtir Post",       "red"),
    "4": ("➕  Auto-Follow ─  Seguir Perfil",     "magenta"),
    "5": ("📋  Ver Contas Salvas",                "yellow"),
    "0": ("🚪  Sair",                             "bright_red"),
}


class InterfaceManager:
    def __init__(self):
        self.console = Console()
        self._logs: list[str] = []
        self._max_logs = 18
        self._color_iter = ASCII_COLOR_CYCLE

    # ─── LOGGING ────────────────────────────────────────────────────────────────

    def log(self, message: str, level: str = "info") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        cfg = {
            "info":    ("cyan",         "ℹ"),
            "success": ("bright_green", "✔"),
            "warning": ("yellow",       "⚠"),
            "error":   ("bright_red",   "✖"),
            "action":  ("magenta",      "⚡"),
        }
        color, prefix = cfg.get(level, ("white", "•"))
        self._logs.append(f"[dim]{ts}[/] [{color}]{prefix} {message}[/]")
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)

    # ─── PAINÉIS ────────────────────────────────────────────────────────────────

    def _header(self, color: str) -> Panel:
        """ASCII animado com cor ciclante + subtítulo premium."""
        art = Text(PHANTOM_ASCII, style=f"bold {color}")
        subtitle = Text(
            "  ◈  Instagram Elite Automation Engine  ◈  Powered by Python 3.12 + Playwright  ◈",
            style="bold white on grey11",
            justify="center",
        )
        content = Align.center(art + Text("\n") + subtitle)
        return Panel(content, border_style=color, padding=(0, 4))

    def _bg_border(self, width: int = 120) -> str:
        """Linha decorativa de fundo ASCII."""
        return BG_TILE * (width // len(BG_TILE) + 1)

    def _menu_panel(self) -> Panel:
        table = Table(show_header=False, expand=True, box=box.SIMPLE, padding=(0, 3))
        table.add_column("K", width=5)
        table.add_column("Opção")
        for key, (label, color) in MENU_OPTIONS.items():
            table.add_row(
                f"[bold {color}][{key}][/]",
                f"[{color}]{label}[/]",
            )
        return Panel(
            table,
            title="[bold bright_cyan]╔═  OPERAÇÕES  ═╗[/]",
            border_style="bright_cyan",
            padding=(1, 2),
        )

    def _log_panel(self) -> Panel:
        content = "\n".join(self._logs) if self._logs else "[dim italic]Aguardando ações...[/]"
        return Panel(
            Text.from_markup(content),
            title="[bold red]▌ LIVE LOGS ▐[/]",
            border_style="red",
            padding=(0, 1),
        )

    def _status_panel(self, stats: dict) -> Panel:
        table = Table(show_header=False, expand=True, box=box.SIMPLE, padding=(0, 1))
        table.add_column("K", style="dim cyan")
        table.add_column("V", style="bold white")
        for k, v in stats.items():
            table.add_row(k, str(v))
        return Panel(table, title="[bold yellow]▌ STATUS ▐[/]", border_style="yellow")

    # ─── TELA PRINCIPAL ANIMADA ─────────────────────────────────────────────────

    def render_home(self, stats: dict) -> None:
        """Renderiza home com ASCII ciclando de cor."""
        color = next(self._color_iter)
        layout = Layout()
        layout.split_column(
            Layout(self._header(color), name="header", size=13),
            Layout(name="body", ratio=1)
        )
        layout["body"].split_row(
            Layout(self._menu_panel(), name="menu", ratio=1),
            Layout(name="right", ratio=1),
        )
        layout["right"].split_column(
            Layout(self._log_panel(), name="logs", ratio=2),
            Layout(self._status_panel(stats), name="status", ratio=1),
        )
        self.console.clear()
        self.console.print(layout)

    # ─── TELA: SEM CONTAS ───────────────────────────────────────────────────────

    def render_no_accounts(self) -> None:
        """Tela premium quando nenhuma conta existe."""
        self.console.clear()
        color = next(self._color_iter)
        header = self._header(color)

        msg = Text.assemble(
            ("\n\n  ⚠  NENHUMA CONTA ENCONTRADA\n\n",     Style(bold=True, color="bright_yellow")),
            ("  Para usar esta função, você precisa criar contas primeiro.\n\n",
             Style(color="white")),
            ("  ➤  Volte ao menu principal\n",             Style(color="cyan")),
            ("  ➤  Selecione a opção  ",                   Style(color="cyan")),
            ("[1] Criar Contas",                            Style(bold=True, color="bright_green")),
            ("\n  ➤  Informe seu e-mail base e a quantidade desejada\n\n",
             Style(color="cyan")),
            ("  O PHANTOM criará as contas em paralelo e salvará\n"
             "  automaticamente no arquivo  data/accounts.json\n\n",
             Style(italic=True, color="dim white")),
        )

        instructions = Panel(
            msg,
            title="[bold bright_yellow]◈  INSTRUÇÕES  ◈[/]",
            border_style="bright_yellow",
            padding=(1, 4),
        )

        layout = Layout()
        layout.split_column(
            Layout(header, name="header", size=14),
            Layout(instructions, name="body"),
        )
        self.console.print(layout)
        self.console.input("\n  [dim]Pressione ENTER para voltar...[/] ")

    # ─── SELETOR DE CONTAS ──────────────────────────────────────────────────────

    def account_selector(self, accounts: list[dict]) -> list[dict]:
        """
        UI interativa de seleção de contas com checkbox.
        Retorna lista de contas selecionadas.
        """
        selected = set(range(len(accounts)))  # todas selecionadas por padrão

        while True:
            self.console.clear()
            color = next(self._color_iter)
            self.console.print(self._header(color))
            self.console.rule("[bold cyan]◈  SELECIONAR CONTAS  ◈[/]")
            self.console.print()

            table = Table(
                show_header=True,
                header_style="bold bright_cyan",
                expand=True,
                box=box.ROUNDED,
                border_style="cyan",
                padding=(0, 2),
            )
            table.add_column("#",         width=4,  justify="center")
            table.add_column("✓",         width=4,  justify="center")
            table.add_column("Username",  style="bold white")
            table.add_column("Email",     style="dim cyan")
            table.add_column("Status",    style="yellow")
            table.add_column("Criado em", style="dim")

            for i, acc in enumerate(accounts):
                mark = "[bright_green]✔[/]" if i in selected else "[dim red]✗[/]"
                row_style = "on grey11" if i in selected else ""
                table.add_row(
                    f"[bold]{i + 1}[/]",
                    mark,
                    f"@{acc['username']}",
                    acc["email"],
                    acc.get("status", "active"),
                    acc.get("created_at", "")[:10],
                    style=row_style,
                )

            self.console.print(table)
            self.console.print()

            # Controles
            controls = Table(show_header=False, box=box.SIMPLE, padding=(0, 3))
            controls.add_column("K", style="bold cyan", width=12)
            controls.add_column("Desc")
            controls.add_row("[A]", "[bright_green]Select All[/]")
            controls.add_row("[D]", "[bright_red]Deselect All[/]")
            controls.add_row("[1-N]", "[white]Toggle conta por número[/]")
            controls.add_row("[ENTER]", "[bold bright_cyan]Confirmar seleção[/]")
            controls.add_row("[0]", "[dim]Cancelar e voltar[/]")
            self.console.print(Panel(controls, border_style="cyan", title="[bold]Controles[/]"))

            choice = self.console.input("\n[bold cyan]❯[/] Comando: ").strip().lower()

            if choice == "a":
                selected = set(range(len(accounts)))
            elif choice == "d":
                selected = set()
            elif choice == "0":
                return []
            elif choice == "":
                if not selected:
                    self.console.print("[yellow]  ⚠ Selecione ao menos uma conta.[/]")
                    time.sleep(1.5)
                    continue
                return [accounts[i] for i in sorted(selected)]
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(accounts):
                        if idx in selected:
                            selected.discard(idx)
                        else:
                            selected.add(idx)
                    else:
                        self.console.print("[red]  Número fora do intervalo.[/]")
                        time.sleep(0.8)
                except ValueError:
                    self.console.print("[red]  Comando inválido.[/]")
                    time.sleep(0.8)

    # ─── HELPERS ────────────────────────────────────────────────────────────────

    def prompt(self, message: str) -> str:
        return self.console.input(f"\n[bold cyan]❯[/] [white]{message}[/] ")

    def print(self, message: str) -> None:
        self.console.print(Text.from_markup(message))

    def rule(self, title: str = "") -> None:
        self.console.rule(f"[bold cyan]{title}[/]")
