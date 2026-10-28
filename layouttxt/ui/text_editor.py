"""Editor de texto de largura fixa (equivale ao RichTextBox `rtxtConteudo`)."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from layouttxt.domain.text_search import TextPosition

CaptureHook = Callable[[str], None]
NAVIGATION_KEYS = frozenset(
    {"Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next", "Escape", "Tab"}
    | {"Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock"}
)
READONLY_SAFE_CONTROL = frozenset({"c", "a", "f", "slash", "Home", "End", "Left", "Right", "Up", "Down"})
CONTROL_MASK = 0x0004
ALT_MASK = 0x20000 if sys.platform == "win32" else 0x0008
FIELD_TAG = "campo"
EQUAL_TAG = "iguais"
CURSOR_TAG = "cursor"


class TextEditor(ttk.Frame):
    """Texto com campo atual sublinhado, marcação de iguais e modo Insere/Sobrescreve.

    O widget fica sempre habilitado; quando não editável, as teclas que
    alteram o texto são bloqueadas (alterações programáticas continuam).

    Exemplo:
        >>> editor = TextEditor(root)  # doctest: +SKIP
        >>> editor.set_content("linha 1\\nlinha 2")  # doctest: +SKIP
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.editable = False
        self.insert_mode = True
        self.on_paste: Callable[[], None] = lambda: None
        self.on_insert_mode_changed: Callable[[bool], None] = lambda _mode: None
        self._capture: CaptureHook | None = None
        self.text = self._build_text()
        self._configure_tags()
        self._bind_keys()

    # ----- conteúdo -------------------------------------------------------
    def content(self) -> str:
        """Todo o texto, com quebras `\\n`."""
        return self.text.get("1.0", "end-1c")

    def lines(self) -> list[str]:
        """Texto dividido em linhas."""
        return self.content().split("\n")

    def line(self, number: int) -> str:
        """Conteúdo da linha 1-based."""
        return self.text.get(f"{number}.0", f"{number}.end")

    def line_count(self) -> int:
        """Quantidade de linhas (inclui a última, mesmo vazia)."""
        return int(self.text.index("end-1c").split(".")[0])

    def set_content(self, content: str, cursor: TextPosition | None = None) -> None:
        """Substitui todo o texto e posiciona o cursor (padrão: início)."""
        view = self.text.yview()[0]
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_reset()
        self.move_cursor(cursor or TextPosition(1, 1))
        if cursor is not None:
            self.text.yview_moveto(view)

    def replace_line(self, number: int, new_line: str) -> None:
        """Troca o conteúdo de uma linha mantendo o cursor."""
        cursor = self.cursor()
        self.text.delete(f"{number}.0", f"{number}.end")
        self.text.insert(f"{number}.0", new_line)
        self.move_cursor(cursor, see=False)

    # ----- cursor ---------------------------------------------------------
    def cursor(self) -> TextPosition:
        """Posição 1-based do cursor."""
        line, char = self.text.index("insert").split(".")
        return TextPosition(int(line), int(char + 1) if isinstance(char, int) else int(char) + 1)

    def move_cursor(self, position: TextPosition, see: bool = True) -> None:
        """Move o cursor (colunas além do fim da linha vão para o fim)."""
        self.text.mark_set("insert", _index(position.line, position.column))
        self.text.tag_remove("sel", "1.0", "end")
        if see:
            self.text.see("insert")

    def select(self, position: TextPosition, length: int) -> None:
        """Seleciona `length` caracteres a partir de `position` e leva o cursor até lá."""
        self.move_cursor(position)
        self.text.tag_add("sel", _index(position.line, position.column), _index(position.line, position.column + length))

    # ----- marcações ------------------------------------------------------
    def highlight_field(self, line: int, start: int, size: int) -> None:
        """Sublinha em vermelho o campo atual."""
        self.text.tag_remove(FIELD_TAG, "1.0", "end")
        self.text.tag_add(FIELD_TAG, _index(line, start), _index(line, start + size))

    def clear_field_highlight(self) -> None:
        """Remove o sublinhado do campo."""
        self.text.tag_remove(FIELD_TAG, "1.0", "end")

    def mark_equal(self, positions: list[TextPosition], length: int) -> None:
        """Pinta de vermelho as ocorrências encontradas por "Marcar iguais"."""
        for position in positions:
            self.text.tag_add(EQUAL_TAG, _index(position.line, position.column), _index(position.line, position.column + length))

    def clear_equal_marks(self) -> None:
        """Remove a marcação de iguais."""
        self.text.tag_remove(EQUAL_TAG, "1.0", "end")

    def set_capture(self, hook: CaptureHook | None) -> None:
        """Enquanto definido, <Enter>/<Esc> no editor chamam `hook(keysym)`."""
        self._capture = hook

    def toggle_insert_mode(self) -> None:
        """Alterna entre Insere e Sobrescreve."""
        self.insert_mode = not self.insert_mode
        self.on_insert_mode_changed(self.insert_mode)

    # ----- construção -----------------------------------------------------
    def _build_text(self) -> tk.Text:
        mono = tkfont.Font(family="Courier New", size=10)
        text = tk.Text(self, wrap="none", undo=True, font=mono, exportselection=False, inactiveselectbackground="#cce")
        vbar = ttk.Scrollbar(self, orient="vertical", command=text.yview)
        hbar = ttk.Scrollbar(self, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        text.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        return text

    def _configure_tags(self) -> None:
        self.text.tag_configure(FIELD_TAG, foreground="red", underline=True)
        self.text.tag_configure(EQUAL_TAG, foreground="red")
        self.text.tag_configure(CURSOR_TAG, background="#c0c0c0")
        self.text.tag_raise("sel")

    def _bind_keys(self) -> None:
        self.text.bind("<Key>", self._on_key)
        for sequence in ("<Control-v>", "<Control-V>", "<Shift-Insert>", "<<Paste>>"):
            self.text.bind(sequence, self._on_paste)
        self.text.bind("<Insert>", self._on_insert_key)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Escape>", self._on_escape)
        self.text.bind("<FocusOut>", self._on_focus_out, add="+")
        self.text.bind("<FocusIn>", self._on_focus_in, add="+")

    # ----- eventos --------------------------------------------------------
    def _on_key(self, event: tk.Event) -> str | None:
        if event.state & ALT_MASK:
            return None
        if event.state & CONTROL_MASK:
            return None if self.editable or event.keysym in READONLY_SAFE_CONTROL else "break"
        if event.keysym in NAVIGATION_KEYS:
            return None
        if not self.editable:
            return "break"
        self._overwrite_if_needed(event)
        return None

    def _overwrite_if_needed(self, event: tk.Event) -> None:
        if self.insert_mode or not event.char or not event.char.isprintable():
            return
        if self.text.tag_ranges("sel") or self.text.compare("insert", "==", "insert lineend"):
            return
        self.text.delete("insert")

    def _on_paste(self, _event: tk.Event) -> str:
        if self.editable:
            self.on_paste()
        else:
            self.bell()
        return "break"

    def _on_insert_key(self, _event: tk.Event) -> str:
        self.toggle_insert_mode()
        return "break"

    def _on_return(self, _event: tk.Event) -> str | None:
        if self._capture is not None:
            self._capture("Return")
            return "break"
        return None if self.editable else "break"

    def _on_escape(self, _event: tk.Event) -> str | None:
        if self._capture is not None:
            self._capture("Escape")
            return "break"
        return None

    def _on_focus_out(self, _event: tk.Event) -> None:
        # Mostra onde o cursor estava enquanto o foco está em outro controle.
        self.text.tag_add(CURSOR_TAG, "insert", "insert+1c")

    def _on_focus_in(self, _event: tk.Event) -> None:
        self.text.tag_remove(CURSOR_TAG, "1.0", "end")


def _index(line: int, column: int) -> str:
    return f"{line}.{max(column, 1) - 1}"
