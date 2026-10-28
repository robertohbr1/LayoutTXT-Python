"""Barra superior de abas e botões de navegação entre registros (`lblMenu`, `cmdProximo`...)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from layouttxt.ui.tooltip import Tooltip

TAB_SPEC: tuple[tuple[int, str], ...] = (
    (0, " Arquivo "),
    (1, " Edita "),
    (3, " Ferramentas "),
    (4, " Substitui "),
    (2, " Lista "),
    (5, " Linhas "),
)


class TopMenuBar(ttk.Frame):
    """Rótulos clicáveis das 6 abas, botões ↓/↑/↓↵/↑↵ e o aviso de captura de bloco."""

    def __init__(
        self,
        master: tk.Misc,
        on_select_tab: Callable[[int], None],
        on_next_line: Callable[[], None],
        on_prev_line: Callable[[], None],
        on_next_type: Callable[[], None],
        on_prev_type: Callable[[], None],
        on_reload_list: Callable[[], None],
    ) -> None:
        super().__init__(master, padding=(4, 4))
        self._on_select_tab = on_select_tab
        self._labels: dict[int, tk.Label] = {}
        self._enabled: dict[int, bool] = {index: True for index, _ in TAB_SPEC}
        self._tabs_frame = ttk.Frame(self)
        self._tabs_frame.pack(side="left")
        self._build_tab_labels()
        self._build_nav_buttons(on_next_line, on_prev_line, on_next_type, on_prev_type, on_reload_list)
        self.message_label = ttk.Label(self, text="", font=("MS Sans Serif", 12))

    def highlight_tab(self, active_index: int) -> None:
        """Destaca em negrito a aba ativa; `-1` esconde as abas e mostra `message_label`."""
        if active_index == -1:
            self._tabs_frame.pack_forget()
            self.reload_btn.pack_forget()
            self.message_label.pack(side="left", padx=6)
            return
        self.message_label.pack_forget()
        self._tabs_frame.pack(side="left")
        for index, label in self._labels.items():
            weight = "bold" if index == active_index else "normal"
            size = 10 if index == active_index else 9
            label.configure(font=("MS Sans Serif", size, weight))
        if active_index == 2:
            self.reload_btn.pack(side="left", padx=8)
        else:
            self.reload_btn.pack_forget()

    def set_tab_enabled(self, index: int, enabled: bool) -> None:
        """Habilita ou desabilita uma aba (ex.: `Lista` sem tipo de linha)."""
        self._enabled[index] = enabled
        self._labels[index].configure(fg="black" if enabled else "#888888")

    def is_tab_enabled(self, index: int) -> bool:
        """True se a aba pode ser aberta."""
        return self._enabled.get(index, False)

    def _build_tab_labels(self) -> None:
        for index, caption in TAB_SPEC:
            label = tk.Label(self._tabs_frame, text=caption, relief="solid", borderwidth=1, padx=4, pady=1)
            label.pack(side="left", padx=2)
            label.bind("<Button-1>", lambda _e, idx=index: self._click(idx))
            self._labels[index] = label

    def _build_nav_buttons(
        self,
        on_next_line: Callable[[], None],
        on_prev_line: Callable[[], None],
        on_next_type: Callable[[], None],
        on_prev_type: Callable[[], None],
        on_reload_list: Callable[[], None],
    ) -> None:
        nav = ttk.Frame(self)
        nav.pack(side="left", padx=16)
        self._nav_button(nav, "↓", "Próximo Registro", on_next_line)
        self._nav_button(nav, "↑", "Registro Anterior", on_prev_line)
        self._nav_button(nav, "↓↵", "Próximo Tipo de Linha", on_next_type, pad_left=12)
        self._nav_button(nav, "↑↵", "Tipo de Linha Anterior", on_prev_type)
        self.reload_btn = ttk.Button(nav, text="Reler", command=on_reload_list)

    def _nav_button(
        self, parent: ttk.Frame, text: str, tip: str, command: Callable[[], None], pad_left: int = 0
    ) -> None:
        btn = ttk.Button(parent, text=text, width=4, command=command)
        btn.pack(side="left", padx=(pad_left, 2))
        Tooltip(btn, tip)

    def _click(self, index: int) -> None:
        if self.is_tab_enabled(index):
            self._on_select_tab(index)
