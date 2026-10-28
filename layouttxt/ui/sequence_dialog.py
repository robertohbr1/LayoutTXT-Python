"""Diálogo modal "Sequenciar" (equivale a `frmSequenciar.frm`)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from layouttxt.domain.line_operations import SequenceOptions
from layouttxt.domain.value_description import vb_val


def ask_sequence_options(parent: tk.Misc, defaults: SequenceOptions) -> SequenceOptions | None:
    """Abre o diálogo modal e retorna as opções confirmadas ou None."""
    dialog = SequenceDialog(parent, defaults)
    parent.wait_window(dialog)
    return dialog.result


class SequenceDialog(tk.Toplevel):
    """Janela modal com os campos Iniciar em, Incrementar, Gerar até, Tamanho e Posição."""

    def __init__(self, parent: tk.Misc, defaults: SequenceOptions) -> None:
        super().__init__(parent)
        self.title("Sequenciar")
        self.resizable(False, False)
        self.transient(parent)
        self.result: SequenceOptions | None = None
        self._start_var = tk.StringVar(value=str(defaults.start))
        self._inc_var = tk.StringVar(value=str(defaults.increment))
        self._end_var = tk.StringVar(value=str(defaults.end))
        self._size_var = tk.StringVar(value=str(defaults.size))
        self._col_var = tk.StringVar(value=str(defaults.column))
        self._end_line_var = tk.BooleanVar(value=defaults.at_line_end)
        self._only_type_var = tk.BooleanVar(value=defaults.only_line_type)
        self._col_entry: ttk.Entry | None = None
        self._build_body()
        self.grab_set()
        self.bind("<Return>", lambda _e: self._confirm())
        self.bind("<Escape>", lambda _e: self.destroy())

    def _build_body(self) -> None:
        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)
        self._add_row(body, 0, "Iniciar em", self._start_var)
        self._add_row(body, 1, "Incrementar", self._inc_var)
        self._add_row(body, 2, "Gerar até", self._end_var)
        self._add_row(body, 3, "Tamanho", self._size_var)
        self._build_position_box(body)
        ttk.Checkbutton(body, text="Somente Linhas do Tipo Atual", variable=self._only_type_var).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(6, 8)
        )
        self._build_buttons(body)

    def _add_row(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=(0, 8), pady=2)
        entry = ttk.Entry(parent, textvariable=variable, width=10, justify="right")
        entry.grid(row=row, column=1, sticky="w", pady=2)
        if row == 0:
            entry.focus_set()
            entry.selection_range(0, "end")

    def _build_position_box(self, parent: ttk.Frame) -> None:
        box = ttk.LabelFrame(parent, text="Fim da Linha", labelwidget=self._end_line_check(parent), padding=6)
        box.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 2))
        ttk.Label(box, text="Posição").pack(side="left", padx=(0, 8))
        self._col_entry = ttk.Entry(box, textvariable=self._col_var, width=10, justify="right")
        self._col_entry.pack(side="left")
        self._toggle_position()

    def _end_line_check(self, parent: ttk.Frame) -> ttk.Checkbutton:
        return ttk.Checkbutton(parent, text="Fim da Linha", variable=self._end_line_var, command=self._toggle_position)

    def _build_buttons(self, parent: ttk.Frame) -> None:
        row = ttk.Frame(parent)
        row.grid(row=6, column=0, columnspan=2, pady=(4, 0))
        ttk.Button(row, text="Ok", width=10, command=self._confirm).pack(side="left", padx=4)
        ttk.Button(row, text="Cancel", width=10, command=self.destroy).pack(side="left", padx=4)

    def _toggle_position(self) -> None:
        if self._col_entry is not None:
            self._col_entry.configure(state="disabled" if self._end_line_var.get() else "normal")

    def _confirm(self) -> None:
        self.result = SequenceOptions(
            start=vb_val(self._start_var.get()),
            increment=max(1, vb_val(self._inc_var.get())),
            end=vb_val(self._end_var.get()),
            size=max(1, vb_val(self._size_var.get())),
            column=max(1, vb_val(self._col_var.get())),
            at_line_end=self._end_line_var.get(),
            only_line_type=self._only_type_var.get(),
        )
        self.destroy()
