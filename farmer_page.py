from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from config import theme
from core.helpers import safe_float
from core.validators import validate_alpha_space, validate_phone, validate_positive_number
from database.repositories import FarmerRepository
from gui.base_page import BasePage


class FarmerPage(BasePage):
    page_title = 'Farmer Profile'
    page_subtitle = 'Maintain farmer records with proper validation and full CRUD support.'

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_id = None
        self.vars = {
            'name': tk.StringVar(),
            'location': tk.StringVar(),
            'phone': tk.StringVar(),
            'farm_size': tk.StringVar(),
            'crop_focus': tk.StringVar(),
        }
        self.errors = {key: tk.StringVar() for key in self.vars}
        self.build_page_header()
        self._build_ui()

    def _build_ui(self):
        form_card = self.section_card(self, 'Farmer Details')
        form_card.pack(fill='x')

        form = tk.Frame(form_card, bg=theme.CARD_BG)
        form.pack(fill='x', padx=14, pady=(0, 14))

        labels = [
            ('Full Name *', 'name'),
            ('Location *', 'location'),
            ('Phone *', 'phone'),
            ('Farm Size (acres) *', 'farm_size'),
            ('Crop Focus', 'crop_focus'),
        ]

        for idx, (label, key) in enumerate(labels):
            tk.Label(
                form,
                text=label,
                bg=theme.CARD_BG,
                fg=theme.TEXT,
                font=theme.BODY_FONT
            ).grid(row=idx, column=0, sticky='w', pady=6)

            tk.Entry(
                form,
                textvariable=self.vars[key],
                width=36,
                font=theme.BODY_FONT,
                relief='solid',
                bd=1
            ).grid(row=idx, column=1, padx=8, pady=6, ipady=5)

            tk.Label(
                form,
                textvariable=self.errors[key],
                bg=theme.CARD_BG,
                fg=theme.DANGER,
                font=theme.SMALL_FONT
            ).grid(row=idx, column=2, sticky='w')

        btns = tk.Frame(form, bg=theme.CARD_BG)
        btns.grid(row=len(labels), column=0, columnspan=3, sticky='w', pady=(10, 0))

        self.primary_button(
            btns,
            'Add Farmer',
            self.add_farmer,
            bg=theme.PRIMARY_LIGHT,
            width=12
        ).pack(side='left', padx=4)

        self.primary_button(
            btns,
            'Update Selected',
            self.update_farmer,
            width=14
        ).pack(side='left', padx=4)

        self.primary_button(
            btns,
            'Delete Selected',
            self.delete_farmer,
            bg=theme.DANGER,
            width=14
        ).pack(side='left', padx=4)

        self.primary_button(
            btns,
            'Clear Form',
            self.clear_form,
            bg='#808b83',
            width=12
        ).pack(side='left', padx=4)

        table_card = self.section_card(self, 'Farmer Records')
        table_card.pack(fill='both', expand=True, pady=(10, 0))

        holder = tk.Frame(table_card, bg=theme.CARD_BG)
        holder.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        cols = ('ID', 'Name', 'Location', 'Phone', 'Farm Size', 'Crop Focus', 'Joined Date')
        self.tree = ttk.Treeview(holder, columns=cols, show='headings', height=14)

        for col, width in zip(cols, [60, 170, 130, 120, 110, 150, 120]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        sb = ttk.Scrollbar(holder, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

    def validate_form(self):
        self.errors['name'].set(validate_alpha_space(self.vars['name'].get(), 'Full name', min_len=3))
        self.errors['location'].set(validate_alpha_space(self.vars['location'].get(), 'Location', min_len=3))
        self.errors['phone'].set(validate_phone(self.vars['phone'].get()))
        self.errors['farm_size'].set(validate_positive_number(self.vars['farm_size'].get(), 'Farm size'))

        focus = self.vars['crop_focus'].get().strip()
        focus_error = ''
        if focus:
            focus_error = validate_alpha_space(focus, 'Crop focus', min_len=2, allow_comma=True)
        self.errors['crop_focus'].set(focus_error)

        return not any(v.get() for v in self.errors.values())

    def on_show(self):
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in FarmerRepository.get_all():
            self.tree.insert('', 'end', values=(
                row['farmer_id'],
                row['full_name'],
                row['location'],
                row['phone'],
                row['farm_size'],
                row.get('crop_focus') or '',
                row['joined_date'],
            ))

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        self.selected_id = values[0]
        self.vars['name'].set(values[1])
        self.vars['location'].set(values[2])
        self.vars['phone'].set(values[3])
        self.vars['farm_size'].set(values[4])
        self.vars['crop_focus'].set(values[5])

        for var in self.errors.values():
            var.set('')

    def add_farmer(self):
        if not self.validate_form():
            return

        FarmerRepository.insert(
            self.vars['name'].get().strip(),
            self.vars['location'].get().strip(),
            self.vars['phone'].get().strip(),
            safe_float(self.vars['farm_size'].get().strip()),
            self.vars['crop_focus'].get().strip(),
        )

        self.clear_form()
        self.load_data()
        messagebox.showinfo('Success', 'Farmer added successfully.')

    def update_farmer(self):
        if not self.selected_id:
            messagebox.showwarning('Update', 'Select a farmer row to update.')
            return

        if not self.validate_form():
            return

        FarmerRepository.update(
            int(self.selected_id),
            self.vars['name'].get().strip(),
            self.vars['location'].get().strip(),
            self.vars['phone'].get().strip(),
            safe_float(self.vars['farm_size'].get().strip()),
            self.vars['crop_focus'].get().strip(),
        )

        self.clear_form()
        self.load_data()
        messagebox.showinfo('Updated', 'Farmer updated successfully.')

    def delete_farmer(self):
        if not self.selected_id:
            messagebox.showwarning('Delete', 'Select a farmer row to delete.')
            return

        if messagebox.askyesno('Confirm Delete', 'Delete this farmer record?'):
            FarmerRepository.delete(int(self.selected_id))
            self.clear_form()
            self.load_data()
            messagebox.showinfo('Deleted', 'Farmer deleted successfully.')

    def clear_form(self):
        self.selected_id = None
        for var in self.vars.values():
            var.set('')
        for err in self.errors.values():
            err.set('')