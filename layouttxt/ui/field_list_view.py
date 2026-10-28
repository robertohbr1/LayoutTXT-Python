"""Grade da aba "Lista" (equivale ao ListView `lstDados` em modo Report)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Sequence

from layouttxt.domain.layout import FieldSpec

COLUMNS: tuple[tuple[str, int], ...] = (
    ("Valor", 360),
    ("Nome", 260),
    ("Inicio", 65),
    ("Tamanho", 75),
    ("Formato", 260),
)


class FieldListView(ttk.Frame):
    """Lista os campos da linha atual e permite editar a coluna Valor (F2 ou digitação).

    Ao sair da lista ou mudar de linha, `rebuilt_line` devolve a linha
    reconstruída concatenando os valores (como `GravaDadosListView`).

    Exemplo:
        >>> view = FieldListView(root)  # doctest: +SKIP
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.editable = True
        self.dirty = False
        self._editor: ttk.Entry | None = None
        self._editing_item = ""
        self.tree = self._build_tree()
        self._bind_events()

    def load_fields(self, line: str, fields: Sequence[FieldSpec]) -> None:
        """Popula a grade com os campos e valores extraídos de `line`."""
        self.commit_inline_edit()
        self.dirty = False
        self.tree.delete(*self.tree.get_children())
        for field in fields:
            values = (field.extract(line), field.name, str(field.start), str(field.size), field.description)
            self.tree.insert("", "end", values=values)
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])

    def rebuilt_line(self) -> str:
        """Concatena a coluna Valor de todos os itens (como `GravaDadosListView`)."""
        self.commit_inline_edit()
        parts: list[str] = []
        for item in self.tree.get_children():
            row = self.tree.item(item, "values")
            size = int(row[3])
            parts.append(str(row[0]).ljust(size)[:size])
        return "".join(parts)

    def commit_inline_edit(self) -> None:
        """Aplica e fecha o Entry de edição inline, se estiver aberto."""
        if self._editor is None:
            return
        new_text = self._editor.get()
        self._close_editor()
        if not self._editing_item or not self.tree.exists(self._editing_item):
            return
        values = list(self.tree.item(self._editing_item, "values"))
        size = int(values[3])
        values[0] = new_text.ljust(size)[:size]
        self.tree.item(self._editing_item, values=values)
        self.dirty = True

    def _build_tree(self) -> ttk.Treeview:
        names = [name for name, _ in COLUMNS]
        tree = ttk.Treeview(self, columns=names, show="headings", selectmode="browse")
        for name, width in COLUMNS:
            tree.heading(name, text=name)
            tree.column(name, width=width, anchor="w" if name != "Inicio" and name != "Tamanho" else "e")
        vbar = ttk.Scrollbar(self, orient="vertical", command=tree.yview)
        hbar = ttk.Scrollbar(self, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        return tree

    def _bind_events(self) -> None:
        self.tree.bind("<F2>", lambda _e: self._start_edit())
        self.tree.bind("<Double-1>", lambda _e: self._start_edit())
        self.tree.bind("<Key>", self._on_key)

    def _on_key(self, event: tk.Event) -> str | None:
        if self.editable and len(event.char) == 1 and ord(event.char) >= 32:
            self._start_edit(initial=event.char)
            return "break"
        return None

    def _start_edit(self, initial: str | None = None) -> None:
        if not self.editable:
            return
        self.commit_inline_edit()
        item = self.tree.focus()
        bbox = self.tree.bbox(item, column="#1") if item else ""
        if not item or not bbox:
            return
        values = self.tree.item(item, "values")
        self._editing_item = item
        self._open_editor(bbox, initial if initial is not None else str(values[0]), int(values[3]))

    def _open_editor(self, bbox: tuple[int, int, int, int], text: str, max_len: int) -> None:
        x, y, width, height = bbox
        validate = (self.register(lambda proposed: len(proposed) <= max_len), "%P")
        self._editor = ttk.Entry(self.tree, validate="key", validatecommand=validate)
        self._editor.place(x=x, y=y, width=width, height=height)
        self._editor.insert(0, text[:max_len])
        self._editor.focus_set()
        if len(text) > 1:
            self._editor.selection_range(0, "end")
        else:
            self._editor.icursor("end")
        self._editor.bind("<Return>", lambda _e: self.commit_inline_edit())
        self._editor.bind("<Escape>", lambda _e: self._close_editor())
        self._editor.bind("<FocusOut>", lambda _e: self.commit_inline_edit())

    def _close_editor(self) -> None:
        if self._editor is not None:
            self._editor.destroy()
            self._editor = None
