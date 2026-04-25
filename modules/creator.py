"""
Account Creator - Criação PARALELA de até 10 contas Instagram
Técnica de sub-endereçamento (user+1@gmail.com)
"""
import asyncio
import random
import string
from datetime import datetime
from faker import Faker
from core.engine import BrowserEngine, HumanBehavior
from modules.data_manager import DataManager, Account

fake = Faker("pt_BR")


class AccountGenerator:
    @staticmethod
    def username() -> str:
        first = fake.first_name().lower().replace(" ", "")
        suffix = random.choice([
            str(random.randint(10, 999)),
            f"_{fake.last_name().lower()[:5]}",
            f".{random.choice(['br', 'oficial', 'real', 'vip'])}",
        ])
        return f"{first}{suffix}"

    @staticmethod
    def password() -> str:
        chars = (
            random.choices(string.ascii_uppercase, k=2) +
            random.choices(string.ascii_lowercase, k=5) +
            random.choices(string.digits, k=3) +
            random.choices("!@#$%", k=1)
        )
        random.shuffle(chars)
        return "".join(chars)

    @staticmethod
    def email(base: str, idx: int) -> str:
        local, domain = base.split("@")
        return f"{local}+{idx}@{domain}"

    @staticmethod
    def birthday() -> tuple[str, str, str]:
        return (
            str(random.randint(1, 28)),
            str(random.randint(1, 12)),
            str(random.randint(1990, 2003)),
        )


class AccountCreator:
    IG_SIGNUP_URL = "https://www.instagram.com/accounts/emailsignup/"

    def __init__(self, ui_log_callback=None):
        self.data_manager = DataManager()
        self.gen = AccountGenerator()
        self.log = ui_log_callback or print

    async def _create_one(self, base_email: str, index: int) -> Account | None:
        """Cria uma única conta (chamado em paralelo)."""
        username = self.gen.username()
        password = self.gen.password()
        email    = self.gen.email(base_email, index)
        name     = fake.name()
        day, month, year = self.gen.birthday()

        self.log(f"[#{index}] Iniciando @{username}", "action")

        engine = BrowserEngine(headless=False)
        try:
            async with engine.new_context() as (context, _browser):
                page = await context.new_page()
                await page.goto(self.IG_SIGNUP_URL, wait_until="networkidle", timeout=30000)
                await HumanBehavior.random_delay(1200, 2500)

                await HumanBehavior.human_type(page, 'input[name="emailOrPhone"]', email)
                await HumanBehavior.human_type(page, 'input[name="fullName"]',     name)
                await HumanBehavior.human_type(page, 'input[name="username"]',     username)
                await HumanBehavior.human_type(page, 'input[name="password"]',     password)
                await HumanBehavior.random_delay(600, 1500)
                await HumanBehavior.human_click(page, 'button[type="submit"]')
                await HumanBehavior.random_delay(2000, 4000)

                # Data de nascimento
                try:
                    await page.select_option('select[title="Dia:"]',  day)
                    await page.select_option('select[title="Mês:"]',  month)
                    await page.select_option('select[title="Ano:"]',  year)
                    await HumanBehavior.random_delay(400, 900)
                    await HumanBehavior.human_click(page, 'button[type="submit"]')
                except Exception:
                    self.log(f"[#{index}] Seletor de data não encontrado", "warning")

                await HumanBehavior.random_delay(2500, 5000)

                account = Account(
                    username=username,
                    password=password,
                    email=email,
                    created_at=datetime.now().isoformat(),
                    status="pending_verification",
                )
                self.data_manager.save_account(account)
                self.log(f"[#{index}] ✔ @{username} criada e salva!", "success")
                return account

        except Exception as e:
            self.log(f"[#{index}] Erro: {str(e)[:70]}", "error")
            return None

    async def create_batch(self, base_email: str, count: int) -> list[Account]:
        """Cria até 10 contas SIMULTANEAMENTE com asyncio.gather."""
        count = min(max(1, count), 10)
        self.log(f"Criando {count} contas em paralelo...", "info")

        tasks = [self._create_one(base_email, i) for i in range(1, count + 1)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        accounts = [r for r in results if isinstance(r, Account)]
        self.log(f"{len(accounts)}/{count} contas criadas com sucesso.", "success")
        return accounts
