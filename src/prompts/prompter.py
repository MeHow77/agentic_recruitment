from pathlib import Path


class Prompter:
    _DIR = Path(__file__).parent

    @staticmethod
    def load(name: str) -> str:
        path = Prompter._DIR / f"{name}.txt"
        return path.read_text(encoding="utf-8")
