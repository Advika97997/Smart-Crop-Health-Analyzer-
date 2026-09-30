from __future__ import annotations

import tkinter as tk

from config import theme


class BasePage(tk.Frame):
    page_title = 'Page'
    page_subtitle = ''

    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG_APP)
        self.controller = controller

    def build_page_header(self):
        header = tk.Frame(self, bg=theme.BG_APP)
        header.pack(fill='x', pady=(0, 10))
        tk.Label(header, text=self.page_title, bg=theme.BG_APP, fg=theme.TEXT, font=theme.HEADER_FONT).pack(anchor='w')
        if self.page_subtitle:
            tk.Label(header, text=self.page_subtitle, bg=theme.BG_APP, fg=theme.MUTED, font=theme.SMALL_FONT).pack(anchor='w', pady=(2, 0))
        return header

    @staticmethod
    def section_card(parent, title: str | None = None, padding: int = 14):
        from config import theme  # local import to avoid circular imports in tooling

        card = tk.Frame(parent, bg=theme.CARD_BG, highlightbackground=theme.BORDER, highlightthickness=1)
        if title:
            tk.Label(card, text=title, bg=theme.CARD_BG, fg=theme.TEXT, font=(theme.FONT_FAMILY, 12, 'bold')).pack(anchor='w', padx=padding, pady=(padding, 8))
        return card

    @staticmethod
    def primary_button(parent, text: str, command, bg=None, fg='white', width=16):
        from config import theme

        button = tk.Button(parent, text=text, command=command, bg=bg or theme.PRIMARY, fg=fg,
                           activebackground=theme.PRIMARY_LIGHT, activeforeground='white', relief='flat',
                           padx=10, pady=8, cursor='hand2', font=theme.BUTTON_FONT, width=width)
        return button
