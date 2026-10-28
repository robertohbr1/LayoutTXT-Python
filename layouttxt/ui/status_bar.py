"""Barra de status inferior (equivale a `StatusBar1` com 13 painéis)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from layouttxt.domain.field_context import FieldContext
from layouttxt.ui.tooltip import Tooltip


class StatusBar(ttk.Frame):
    """Mostra Início, Tamanho, Tipo, Lin, Col, Formato e modo Insere/Sobrescreve.

    Os painéis Lin, Col e Insere são clicáveis, como no VB.

    Exemplo:
        >>> bar = StatusBar(root, lambda: None, lambda: None, lambda: None)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        on_line_click: Callable[[], None],
        on_col_click: Callable[[], None],
        on_insert_click: Callable[[], None],
    ) -> None:
        super().__init__(master, relief="sunken", padding=(2, 1))
        self._start_var = tk.StringVar()
        self._size_var = tk.StringVar()
        self._type_var = tk.StringVar()
        self._line_var = tk.StringVar()
        self._col_var = tk.StringVar()
        self._format_var = tk.StringVar()
        self._insert_var = tk.StringVar(value=" Insere ")
        self._build_panels(on_line_click, on_col_click, on_insert_click)

    def update_from(self, context: FieldContext) -> None:
        """Atualiza todos os painéis a partir do `FieldContext` atual."""
        self._line_var.set(str(context.line_number))
        self._col_var.set(str(context.column))
        self._type_var.set(context.record_id)
        self._start_var.set(str(context.field.start) if context.field else "")
        self._size_var.set(str(context.field.size) if context.field else "")
        self._format_var.set(context.field.description if context.field else "")

    def clear_position(self) -> None:
        """Limpa Lin e Col quando o texto está vazio."""
        self._line_var.set("")
        self._col_var.set("")
        self._type_var.set("")
        self._start_var.set("")
        self._size_var.set("")
        self._format_var.set("")

    def set_insert_mode(self, insert_mode: bool) -> None:
        """Atualiza o painel `Insere`/`Sobrescreve`."""
        self._insert_var.set(" Insere " if insert_mode else " Sobrescreve ")

    def _build_panels(
        self,
        on_line_click: Callable[[], None],
        on_col_click: Callable[[], None],
        on_insert_click: Callable[[], None],
    ) -> None:
        self._add_pair("Inicio", self._start_var, 6, "Coluna Inicial")
        self._add_pair("  Tamanho", self._size_var, 5, "Tamanho do Campo")
        self._add_pair("  Tipo", self._type_var, 8, "Tipo de Linha")
        line_box = self._add_pair("  Lin", self._line_var, 6, "Linha Atual - Clique aqui para alterar")
        col_box = self._add_pair("  Col", self._col_var, 6, "Coluna atual - Clique aqui para alterar")
        self._add_format_panel()
        insert_box = self._add_box(self._insert_var, 12, "Modo de edição", side="right")
        line_box.bind("<Button-1>", lambda _e: on_line_click())
        col_box.bind("<Button-1>", lambda _e: on_col_click())
        insert_box.bind("<Button-1>", lambda _e: on_insert_click())

    def _add_pair(self, title: str, variable: tk.StringVar, width: int, tip: str) -> ttk.Label:
        ttk.Label(self, text=title).pack(side="left", padx=(4, 2))
        return self._add_box(variable, width, tip)

    def _add_box(self, variable: tk.StringVar, width: int, tip: str, side: str = "left") -> ttk.Label:
        label = ttk.Label(self, textvariable=variable, width=width, relief="sunken", anchor="center")
        label.pack(side=side, padx=2, fill="y")
        Tooltip(label, tip)
        return label

    def _add_format_panel(self) -> None:
        ttk.Label(self, text="  Formato").pack(side="left", padx=(4, 2))
        label = ttk.Label(self, textvariable=self._format_var, relief="sunken", anchor="w")
        label.pack(side="left", padx=2, fill="x", expand=True)
        Tooltip(label, "Formato do Campo")
