from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from config import theme
from core.helpers import truncate
from gui.base_page import BasePage
from services.dashboard_service import DashboardService


class DashboardPage(BasePage):
    page_title = 'Dashboard'
    page_subtitle = 'View system activity, crop health analytics, and recent analysis history.'

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.total_analyses_var = tk.StringVar(value='0')
        self.avg_health_var = tk.StringVar(value='0')
        self.healthy_count_var = tk.StringVar(value='0')
        self.total_crops_var = tk.StringVar(value='0')
        self.total_farmers_var = tk.StringVar(value='0')

        self.build_page_header()
        self._build_ui()

    def _build_ui(self):
        # ===== Top summary cards =====
        cards_row = tk.Frame(self, bg=theme.BG_APP)
        cards_row.pack(fill='x', pady=(0, 8))

        self._make_stat_card(cards_row, 'Total Analyses', self.total_analyses_var).pack(
            side='left', fill='x', expand=True, padx=(0, 8)
        )
        self._make_stat_card(cards_row, 'Average Health Score', self.avg_health_var).pack(
            side='left', fill='x', expand=True, padx=4
        )
        self._make_stat_card(cards_row, 'Healthy Count', self.healthy_count_var).pack(
            side='left', fill='x', expand=True, padx=4
        )
        self._make_stat_card(cards_row, 'Total Crops', self.total_crops_var).pack(
            side='left', fill='x', expand=True, padx=4
        )
        self._make_stat_card(cards_row, 'Total Farmers', self.total_farmers_var).pack(
            side='left', fill='x', expand=True, padx=(4, 0)
        )

        # ===== Charts row =====
        charts_row = tk.Frame(self, bg=theme.BG_APP)
        charts_row.pack(fill='x', pady=(0, 8))

        status_card = self.section_card(charts_row, 'Health Status Distribution')
        status_card.pack(side='left', fill='both', expand=True, padx=(0, 8))

        self.status_canvas = tk.Canvas(
            status_card,
            bg='#f6fbf7',
            height=180,
            highlightthickness=0
        )
        self.status_canvas.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        crop_card = self.section_card(charts_row, 'Analyses by Crop')
        crop_card.pack(side='left', fill='both', expand=True)

        self.crop_canvas = tk.Canvas(
            crop_card,
            bg='#f6fbf7',
            height=180,
            highlightthickness=0
        )
        self.crop_canvas.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        # ===== Recent uploads =====
        recent_card = self.section_card(self, 'Recent Uploads')
        recent_card.pack(fill='both', expand=True)

        holder = tk.Frame(recent_card, bg=theme.CARD_BG)
        holder.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        cols = ('Crop', 'Status', 'Score', 'Analyzed On')
        self.tree = ttk.Treeview(holder, columns=cols, show='headings', height=8)

        widths = [180, 140, 110, 180]
        for col, width in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        sb = ttk.Scrollbar(holder, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

    def _make_stat_card(self, parent, title: str, value_var: tk.StringVar):
        card = tk.Frame(parent, bg=theme.CARD_BG, bd=1, relief='solid')

        tk.Label(
            card,
            text=title,
            bg=theme.CARD_BG,
            fg=theme.MUTED,
            font=theme.SMALL_FONT
        ).pack(anchor='w', padx=12, pady=(10, 2))

        tk.Label(
            card,
            textvariable=value_var,
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.TITLE_FONT
        ).pack(anchor='w', padx=12, pady=(0, 10))

        return card

    def on_show(self):
        self.refresh()

    def refresh(self):
        summary = DashboardService.get_summary()
        self.total_analyses_var.set(str(summary.get('total_analyses', 0)))
        self.avg_health_var.set(str(summary.get('avg_health_score', 0)))
        self.healthy_count_var.set(str(summary.get('healthy_count', 0)))
        self.total_crops_var.set(str(summary.get('total_crops', 0)))
        self.total_farmers_var.set(str(summary.get('total_farmers', 0)))

        self._draw_bar_chart(
            self.status_canvas,
            DashboardService.get_status_distribution(),
            'Status'
        )
        self._draw_bar_chart(
            self.crop_canvas,
            DashboardService.get_crop_distribution(),
            'Crop'
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in DashboardService.get_recent_uploads():
            self.tree.insert('', 'end', values=(
                row.get('crop_name', ''),
                row.get('health_status', ''),
                row.get('health_score', ''),
                str(row.get('analyzed_on', ''))[:19],
            ))

        self.controller.set_status('Dashboard loaded successfully.')

    def _draw_bar_chart(self, canvas: tk.Canvas, data: dict, label_prefix: str):
        canvas.delete('all')
        canvas.update_idletasks()

        width = max(canvas.winfo_width(), 320)
        height = max(canvas.winfo_height(), 180)

        if not data:
            canvas.create_text(
                width // 2,
                height // 2,
                text='No data available',
                fill=theme.MUTED,
                font=theme.BODY_FONT
            )
            return

        items = list(data.items())
        max_value = max(v for _, v in items) or 1

        left_margin = 45
        bottom_margin = 35
        top_margin = 20
        right_margin = 20

        usable_width = width - left_margin - right_margin
        usable_height = height - top_margin - bottom_margin

        bar_gap = 16
        bar_width = max(22, int((usable_width - (bar_gap * (len(items) - 1))) / max(len(items), 1)))

        x = left_margin

        for label, value in items:
            bar_height = int((value / max_value) * usable_height)
            y1 = height - bottom_margin - bar_height
            y2 = height - bottom_margin

            canvas.create_rectangle(
                x, y1, x + bar_width, y2,
                fill=theme.PRIMARY,
                outline=''
            )

            canvas.create_text(
                x + bar_width / 2,
                y1 - 10,
                text=str(value),
                fill=theme.TEXT,
                font=theme.SMALL_FONT
            )

            canvas.create_text(
                x + bar_width / 2,
                height - 15,
                text=truncate(str(label), 10),
                fill=theme.MUTED,
                font=('Segoe UI', 8)
            )

            x += bar_width + bar_gap