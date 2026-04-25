"""
Engine - Motor de Automação com Playwright + Stealth
Comportamento humano: delays, movimentos de mouse, variação de cliques
"""
import asyncio
import random
import math
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page, BrowserContext
from playwright_stealth import stealth_async


class HumanBehavior:
    """Simula comportamento humano para evitar detecção."""

    @staticmethod
    async def random_delay(min_ms: float = 800, max_ms: float = 2500) -> None:
        """Pausa randômica entre ações."""
        delay = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)

    @staticmethod
    async def smooth_mouse_move(page: Page, x: int, y: int, steps: int = 25) -> None:
        """Move o mouse em curva de Bézier para parecer humano."""
        curr_pos = await page.evaluate("() => ({x: window.mouseX || 0, y: window.mouseY || 0})")
        cx, cy = curr_pos.get("x", 0), curr_pos.get("y", 0)

        # Pontos de controle da curva Bézier
        ctrl1_x = cx + random.randint(-100, 100)
        ctrl1_y = cy + random.randint(-50, 50)
        ctrl2_x = x + random.randint(-100, 100)
        ctrl2_y = y + random.randint(-50, 50)

        for i in range(steps + 1):
            t = i / steps
            # Fórmula cúbica de Bézier
            bx = (1-t)**3*cx + 3*(1-t)**2*t*ctrl1_x + 3*(1-t)*t**2*ctrl2_x + t**3*x
            by = (1-t)**3*cy + 3*(1-t)**2*t*ctrl1_y + 3*(1-t)*t**2*ctrl2_y + t**3*y
            await page.mouse.move(int(bx), int(by))
            await asyncio.sleep(random.uniform(0.005, 0.02))

    @staticmethod
    async def human_click(page: Page, selector: str) -> None:
        """Clique com movimento de mouse + delay humano."""
        element = await page.wait_for_selector(selector, timeout=10000)
        box = await element.bounding_box()
        if box:
            # Clica em posição randômica dentro do elemento (não no centro exato)
            x = box["x"] + random.uniform(box["width"] * 0.2, box["width"] * 0.8)
            y = box["y"] + random.uniform(box["height"] * 0.2, box["height"] * 0.8)
            await HumanBehavior.smooth_mouse_move(page, int(x), int(y))
            await HumanBehavior.random_delay(200, 600)
            await page.mouse.click(int(x), int(y))
        await HumanBehavior.random_delay(500, 1200)

    @staticmethod
    async def human_type(page: Page, selector: str, text: str) -> None:
        """Digita texto com velocidade variável como humano."""
        await HumanBehavior.human_click(page, selector)
        for char in text:
            await page.keyboard.type(char, delay=random.uniform(60, 220))
        await HumanBehavior.random_delay(300, 800)

    @staticmethod
    async def random_scroll(page: Page) -> None:
        """Scroll randômico para simular leitura."""
        scroll_amount = random.randint(200, 600)
        direction = random.choice([1, -1])
        await page.mouse.wheel(0, scroll_amount * direction)
        await HumanBehavior.random_delay(400, 1000)


class BrowserEngine:
    """Motor de automação baseado em Playwright com perfil stealth."""

    MOBILE_USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    ]

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.human = HumanBehavior()

    @asynccontextmanager
    async def new_context(self):
        """Cria contexto de navegador isolado com fingerprint único."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--lang=pt-BR,pt;q=0.9,en;q=0.8",
                ],
            )
            context = await browser.new_context(
                user_agent=random.choice(self.MOBILE_USER_AGENTS),
                viewport={"width": 390, "height": 844},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                geolocation={"latitude": -23.5505, "longitude": -46.6333},
                permissions=["geolocation"],
                color_scheme="dark",
            )
            # Injeta scripts anti-detecção
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt']});
                window.chrome = {runtime: {}};
            """)
            try:
                yield context, browser
            finally:
                await browser.close()
