from abc import ABC, abstractmethod
from collections.abc import Sequence

import questionary


class Console(ABC):
    """Abstract base class for CLI interaction."""

    @abstractmethod
    def print(self, message: str, style: str = "") -> None:
        """Print a message to the console."""
        ...

    @abstractmethod
    async def input(self, prompt: str) -> str:
        """Get free-form text input from the user."""
        ...

    @abstractmethod
    async def confirm(self, prompt: str, default: bool = False) -> bool:
        """Ask a yes/no confirmation question."""
        ...

    @abstractmethod
    async def select(self, prompt: str, options: Sequence[str]) -> str:
        """Present a selection menu and return the chosen option."""
        ...


class QuestionaryConsole(Console):
    """Rich CLI implementation using questionary for styled prompts."""

    def print(self, message: str, style: str = "") -> None:
        if style:
            questionary.print(message, style=style)
        else:
            print(message)

    async def input(self, prompt: str) -> str:
        result = await questionary.text(prompt).ask_async()
        return result if result is not None else ""

    async def confirm(self, prompt: str, default: bool = False) -> bool:
        result = await questionary.confirm(prompt, default=default).ask_async()
        return result if result is not None else default

    async def select(self, prompt: str, options: Sequence[str]) -> str:
        result = await questionary.select(prompt, choices=list(options)).ask_async()
        return result if result is not None else options[0] if options else ""


class MockConsole(Console):
    """Test double with pre-programmed responses."""

    def __init__(
        self,
        inputs: Sequence[str] | None = None,
        confirms: Sequence[bool] | None = None,
        selects: Sequence[str] | None = None,
    ) -> None:
        self._inputs = list(inputs or [])
        self._confirms = list(confirms or [])
        self._selects = list(selects or [])
        self._input_index = 0
        self._confirm_index = 0
        self._select_index = 0
        self.printed: list[tuple[str, str]] = []

    def print(self, message: str, style: str = "") -> None:
        self.printed.append((message, style))

    async def input(self, prompt: str) -> str:
        if self._input_index < len(self._inputs):
            result = self._inputs[self._input_index]
            self._input_index += 1
            return result
        return ""

    async def confirm(self, prompt: str, default: bool = False) -> bool:
        if self._confirm_index < len(self._confirms):
            result = self._confirms[self._confirm_index]
            self._confirm_index += 1
            return result
        return default

    async def select(self, prompt: str, options: Sequence[str]) -> str:
        if self._select_index < len(self._selects):
            result = self._selects[self._select_index]
            self._select_index += 1
            return result
        return options[0] if options else ""
