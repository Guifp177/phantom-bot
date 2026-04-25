"""
Data Manager - Gerenciador de Contas JSON
Salva, carrega e exibe contas criadas
"""
import json
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel


DATA_FILE = Path(__file__).parent.parent / "data" / "accounts.json"


class Account(BaseModel):
    username: str
    password: str
    email: str
    created_at: str
    status: str = "active"


class DataManager:
    """Gerencia persistência de contas em accounts.json."""

    def __init__(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            DATA_FILE.write_text("[]", encoding="utf-8")

    def load_all(self) -> list[Account]:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Account(**item) for item in raw]

    def save_account(self, account: Account) -> None:
        accounts = self.load_all()
        # Evita duplicatas por username
        accounts = [a for a in accounts if a.username != account.username]
        accounts.append(account)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([a.model_dump() for a in accounts], f, indent=2, ensure_ascii=False)

    def get_count(self) -> int:
        return len(self.load_all())

    def display_table(self) -> list[dict]:
        """Retorna contas como lista de dicts para exibição."""
        return [a.model_dump() for a in self.load_all()]
