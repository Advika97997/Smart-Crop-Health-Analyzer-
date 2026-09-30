from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from config import settings, theme
from core.validators import validate_required
from database.repositories import UserRepository


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.SIDEBAR_BG)
        self.controller = controller
        self.username_var = tk.StringVar(value=settings.DEFAULT_USERNAME)
        self.password_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        wrapper = tk.Frame(self, bg=theme.SIDEBAR_BG)
        wrapper.pack(fill='both', expand=True, padx=20, pady=20)

        left = tk.Frame(wrapper, bg=theme.SIDEBAR_BG)
        left.pack(side='left', fill='both', expand=True)
        tk.Label(left, text='Crop Health Analyzer', bg=theme.SIDEBAR_BG, fg='white', font=(theme.FONT_FAMILY, 30, 'bold')).pack(anchor='w', pady=(120, 8))
        tk.Label(left, text='Image-Based Farming Solution', justify='left', bg=theme.SIDEBAR_BG, fg='#d6f3e2', font=(theme.FONT_FAMILY, 14)).pack(anchor='w')
        tk.Label(left, text='Core Highlights\n• Tkinter multi-page UI\n• MySQL database\n• Full CRUD operations\n• OpenCV image processing\n• Smart crop advice engine', justify='left', bg=theme.SIDEBAR_BG, fg='white', font=theme.BODY_FONT).pack(anchor='w', pady=(30, 0))

        card = tk.Frame(wrapper, bg=theme.CARD_BG, highlightbackground=theme.BORDER, highlightthickness=1, padx=36, pady=32)
        card.pack(side='right', padx=(20, 60), pady=80)

        tk.Label(card, text='Login', bg=theme.CARD_BG, fg=theme.TEXT, font=(theme.FONT_FAMILY, 22, 'bold')).pack(anchor='w')
        tk.Label(card, text='Use the admin credentials from schema.sql', bg=theme.CARD_BG, fg=theme.MUTED, font=theme.SMALL_FONT).pack(anchor='w', pady=(4, 18))

        self._field(card, 'Username', self.username_var)
        self._field(card, 'Password', self.password_var, show='*')

        tk.Label(card, textvariable=self.error_var, bg=theme.CARD_BG, fg=theme.DANGER, font=theme.SMALL_FONT).pack(anchor='w', pady=(6, 6))

        tk.Button(card, text='Login', command=self.login, bg=theme.PRIMARY, fg='white', activebackground=theme.PRIMARY_LIGHT,
                  activeforeground='white', relief='flat', font=theme.BUTTON_FONT, padx=10, pady=10, cursor='hand2').pack(fill='x', pady=(8, 8))
        tk.Label(card, text='Default password: admin123', bg=theme.CARD_BG, fg=theme.MUTED, font=theme.SMALL_FONT).pack(anchor='w')
        self.bind_all('<Return>', lambda _e: self.login())

    def _field(self, parent, label: str, variable: tk.StringVar, show: str | None = None):
        tk.Label(parent, text=label, bg=theme.CARD_BG, fg=theme.TEXT, font=theme.BODY_FONT).pack(anchor='w', pady=(6, 4))
        entry = tk.Entry(parent, textvariable=variable, show=show or '', width=30, font=(theme.FONT_FAMILY, 11), relief='solid', bd=1)
        entry.pack(fill='x', ipady=7)
        return entry

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        self.error_var.set(validate_required(username, 'Username') or validate_required(password, 'Password'))
        if self.error_var.get():
            return
        try:
            user = UserRepository.authenticate(username, password)
            if not user:
                self.error_var.set('Invalid username or password.')
                return
            self.controller.login_success(user)
        except Exception as exc:
            messagebox.showerror('Login Error', str(exc))
