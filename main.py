"""
PHANTOM BOT - main.py
Ponto de entrada principal — Menu interativo com Rich
"""
import asyncio
import sys
import os

# Garante que o diretório raiz está no path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from rich import box

from core.interface import InterfaceManager
from modules.data_manager import DataManager, Account
from modules.creator import AccountCreator
from modules.engagement import EngagementBot

console = Console()
ui = InterfaceManager()
db = DataManager()


# ─── HELPERS ────────────────────────────────────────────────────────────────────

def _get_stats() -> dict:
    return {
        "Contas salvas":  str(db.get_count()),
        "Versão do Bot":  "PHANTOM v1.0",
        "Engine":         "Playwright",
        "Modo":           "Stealth",
    }


def _get_accounts_or_warn() -> list[dict] | None:
    """Retorna contas salvas ou exibe tela de instrução e retorna None."""
    accounts = db.display_table()
    if not accounts:
        ui.render_no_accounts()
        return None
    return accounts


def _accounts_to_model(raw: list[dict]) -> list[Account]:
    return [Account(**a) for a in raw]


def _show_accounts_table(accounts: list[dict]) -> None:
    """Exibe tabela de contas salvas de forma premium."""
    console.clear()
    ui.rule("CONTAS SALVAS")
    table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        expand=True,
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("#",         width=4, justify="center")
    table.add_column("Username",  style="bold white")
    table.add_column("Senha",     style="dim yellow")
    table.add_column("Email",     style="cyan")
    table.add_column("Status",    style="green")
    table.add_column("Criado em", style="dim")

    for i, acc in enumerate(accounts, 1):
        table.add_row(
            str(i),
            f"@{acc['username']}",
            acc["password"],
            acc["email"],
            acc.get("status", "active"),
            acc.get("created_at", "")[:10],
        )
    console.print(table)
    console.input("\n[dim]Pressione ENTER para voltar...[/] ")


# ─── HANDLERS DE MENU ───────────────────────────────────────────────────────────

async def handle_create_accounts() -> None:
    console.clear()
    ui.rule("CRIAR CONTAS — MODO PARALELO")

    base_email = ui.prompt("Informe seu e-mail base (ex: seuemail@gmail.com):")
    if "@" not in base_email:
        ui.print("[red]  ✖ E-mail inválido.[/]")
        await asyncio.sleep(2)
        return

    count_str = ui.prompt("Quantas contas criar? (1-10):")
    try:
        count = int(count_str)
        if not 1 <= count <= 10:
            raise ValueError
    except ValueError:
        ui.print("[red]  ✖ Número inválido. Use entre 1 e 10.[/]")
        await asyncio.sleep(2)
        return

    ui.log(f"Iniciando criação de {count} contas em paralelo...", "info")

    creator = AccountCreator(ui_log_callback=ui.log)
    ui.render_home(_get_stats())

    accounts = await creator.create_batch(base_email, count)

    ui.log(f"Concluído: {len(accounts)} contas criadas.", "success")
    await asyncio.sleep(3)


async def handle_auto_view() -> None:
    raw = _get_accounts_or_warn()
    if raw is None:
        return

    selected_raw = ui.account_selector(raw)
    if not selected_raw:
        return

    console.clear()
    ui.rule("AUTO-VIEW")
    target = ui.prompt("URL do vídeo/story/reel:")
    if not target.startswith("http"):
        ui.print("[red]  ✖ URL inválida.[/]")
        await asyncio.sleep(2)
        return

    selected = _accounts_to_model(selected_raw)
    ui.log(f"Iniciando Auto-View com {len(selected)} contas...", "action")
    ui.render_home(_get_stats())

    bot = EngagementBot(ui_log_callback=ui.log)
    await bot.auto_view(selected, target)

    ui.log("Auto-View concluído!", "success")
    await asyncio.sleep(3)


async def handle_auto_like() -> None:
    raw = _get_accounts_or_warn()
    if raw is None:
        return

    selected_raw = ui.account_selector(raw)
    if not selected_raw:
        return

    console.clear()
    ui.rule("AUTO-LIKE")
    target = ui.prompt("URL do post para curtir:")
    if not target.startswith("http"):
        ui.print("[red]  ✖ URL inválida.[/]")
        await asyncio.sleep(2)
        return

    selected = _accounts_to_model(selected_raw)
    ui.log(f"Iniciando Auto-Like com {len(selected)} contas...", "action")
    ui.render_home(_get_stats())

    bot = EngagementBot(ui_log_callback=ui.log)
    await bot.auto_like(selected, target)

    ui.log("Auto-Like concluído!", "success")
    await asyncio.sleep(3)


async def handle_auto_follow() -> None:
    raw = _get_accounts_or_warn()
    if raw is None:
        return

    selected_raw = ui.account_selector(raw)
    if not selected_raw:
        return

    console.clear()
    ui.rule("AUTO-FOLLOW")
    target = ui.prompt("Username do perfil alvo (ex: @neymarjr ou neymarjr):")

    selected = _accounts_to_model(selected_raw)
    ui.log(f"Iniciando Auto-Follow em @{target.lstrip('@')} com {len(selected)} contas...", "action")
    ui.render_home(_get_stats())

    bot = EngagementBot(ui_log_callback=ui.log)
    await bot.auto_follow(selected, target)

    ui.log("Auto-Follow concluído!", "success")
    await asyncio.sleep(3)


async def handle_view_accounts() -> None:
    raw = db.display_table()
    if not raw:
        ui.render_no_accounts()
        return
    _show_accounts_table(raw)


# ─── LOOP PRINCIPAL ─────────────────────────────────────────────────────────────

HANDLERS = {
    "1": handle_create_accounts,
    "2": handle_auto_view,
    "3": handle_auto_like,
    "4": handle_auto_follow,
    "5": handle_view_accounts,
}


async def main() -> None:
    ui.log("PHANTOM BOT iniciado.", "success")
    ui.log("Ambiente carregado com sucesso.", "info")

    while True:
        ui.render_home(_get_stats())
        choice = ui.prompt("Escolha uma opção:").strip()

        if choice == "0":
            console.clear()
            ui.print("\n[bold bright_magenta]  ◈  PHANTOM encerrado. Até logo.  ◈[/]\n")
            break

        handler = HANDLERS.get(choice)
        if handler:
            ui.log(f"Opção [{choice}] selecionada.", "action")
            await handler()
        else:
            ui.log("Opção inválida. Tente novamente.", "warning")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
