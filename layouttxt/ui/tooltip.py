"""Dica flutuante (ToolTipText do VB) para widgets Tk."""

from __future__ import annotations

import tkinter as tk

_DELAY_MS = 500


class Tooltip:
    """Mostra `text` após o mouse parar sobre o widget.

    Exemplo:
        >>> Tooltip(button, "Próximo Registro")  # doctest: +SKIP
    """

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self.text = text
        self._window: tk.Toplevel | None = None
        self._pending: str | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event: tk.Event) -> None:
        self._cancel()
        self._pending = self._widget.after(_DELAY_MS, self._show)

    def _show(self) -> None:
        if not self.text:
            return
        self._window = tk.Toplevel(self._widget)
        self._window.wm_overrideredirect(True)
        x = self._widget.winfo_rootx() + 10
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._window.wm_geometry(f"+{x}+{y}")
        tk.Label(self._window, text=self.text, background="#ffffe0", relief="solid", borderwidth=1).pack()

    def _hide(self, _event: tk.Event | None = None) -> None:
        self._cancel()
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def _cancel(self) -> None:
        if self._pending is not None:
            self._widget.after_cancel(self._pending)
            self._pending = None
