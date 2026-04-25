"""
Engagement Module - Auto-View, Auto-Like, Auto-Follow
Execução PARALELA nas contas selecionadas
"""
import asyncio
import random
from core.engine import BrowserEngine, HumanBehavior
from modules.data_manager import Account


class EngagementBot:
    IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"

    def __init__(self, ui_log_callback=None):
        self.log = ui_log_callback or print

    async def _login(self, page, account: Account) -> bool:
        self.log(f"Login: @{account.username}...", "action")
        try:
            await page.goto(self.IG_LOGIN_URL, wait_until="networkidle", timeout=30000)
            await HumanBehavior.random_delay(1500, 3000)

            # Fecha popup de cookies se aparecer
            try:
                await page.click('button:has-text("Recusar")', timeout=3000)
            except Exception:
                pass

            await HumanBehavior.human_type(page, 'input[name="username"]', account.username)
            await HumanBehavior.human_type(page, 'input[name="password"]', account.password)
            await HumanBehavior.random_delay(600, 1400)
            await HumanBehavior.human_click(page, 'button[type="submit"]')
            await HumanBehavior.random_delay(4000, 7000)

            if "/login" not in page.url:
                self.log(f"✔ @{account.username} logado!", "success")
                return True
            self.log(f"✖ Falha no login de @{account.username}", "error")
            return False
        except Exception as e:
            self.log(f"✖ Erro login @{account.username}: {str(e)[:55]}", "error")
            return False

    # ─── AUTO-VIEW ──────────────────────────────────────────────────────────────

    async def _view_one(self, account: Account, target_url: str) -> None:
        engine = BrowserEngine(headless=False)
        async with engine.new_context() as (context, _):
            page = await context.new_page()
            if not await self._login(page, account):
                return
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            await HumanBehavior.random_delay(2000, 4000)
            for _ in range(random.randint(2, 5)):
                await HumanBehavior.random_scroll(page)
            view_time = random.uniform(8, 22)
            self.log(f"👁  @{account.username} assistindo {view_time:.0f}s...", "info")
            await asyncio.sleep(view_time)
            self.log(f"✔ View concluído: @{account.username}", "success")

    async def auto_view(self, accounts: list[Account], target_url: str) -> None:
        self.log(f"Auto-View em {len(accounts)} contas simultaneamente...", "action")
        await asyncio.gather(*[self._view_one(a, target_url) for a in accounts])

    # ─── AUTO-LIKE ──────────────────────────────────────────────────────────────

    async def _like_one(self, account: Account, target_url: str) -> None:
        engine = BrowserEngine(headless=False)
        async with engine.new_context() as (context, _):
            page = await context.new_page()
            if not await self._login(page, account):
                return
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            await HumanBehavior.random_delay(2000, 5000)
            await HumanBehavior.random_scroll(page)
            try:
                await HumanBehavior.human_click(page, 'svg[aria-label="Curtir"]')
                self.log(f"❤  @{account.username} curtiu!", "success")
            except Exception:
                try:
                    await HumanBehavior.human_click(page, 'svg[aria-label="Like"]')
                    self.log(f"❤  @{account.username} curtiu!", "success")
                except Exception:
                    self.log(f"⚠  Botão like não encontrado para @{account.username}", "warning")

    async def auto_like(self, accounts: list[Account], target_url: str) -> None:
        self.log(f"Auto-Like em {len(accounts)} contas simultaneamente...", "action")
        await asyncio.gather(*[self._like_one(a, target_url) for a in accounts])

    # ─── AUTO-FOLLOW ────────────────────────────────────────────────────────────

    async def _follow_one(self, account: Account, target_profile: str) -> None:
        profile_url = f"https://www.instagram.com/{target_profile.lstrip('@')}/"
        engine = BrowserEngine(headless=False)
        async with engine.new_context() as (context, _):
            page = await context.new_page()
            if not await self._login(page, account):
                return
            await page.goto(profile_url, wait_until="networkidle", timeout=30000)
            await HumanBehavior.random_delay(2000, 5000)
            try:
                await HumanBehavior.human_click(page, 'button:has-text("Seguir")')
                self.log(f"➕ @{account.username} seguiu @{target_profile}!", "success")
            except Exception:
                try:
                    await HumanBehavior.human_click(page, 'button:has-text("Follow")')
                    self.log(f"➕ @{account.username} seguiu @{target_profile}!", "success")
                except Exception:
                    self.log(f"⚠  Botão Follow não encontrado para @{account.username}", "warning")

    async def auto_follow(self, accounts: list[Account], target_profile: str) -> None:
        self.log(f"Auto-Follow em {len(accounts)} contas simultaneamente...", "action")
        await asyncio.gather(*[self._follow_one(a, target_profile) for a in accounts])
