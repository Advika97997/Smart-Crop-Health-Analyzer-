from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from config import theme
from core.validators import validate_alpha_space
from database.repositories import CropRepository
from gui.base_page import BasePage


class CropsPage(BasePage):
    page_title = 'Manage Crops'
    page_subtitle = 'Add, update, and delete crop master records used during analysis.'

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_id = None
        self.crop_name_var = tk.StringVar()
        self.species_var = tk.StringVar()
        self.crop_error = tk.StringVar()
        self.species_error = tk.StringVar()
        self.build_page_header()
        self._build_ui()

    def _build_ui(self):
        top = self.section_card(self, 'Crop Form')
        top.pack(fill='x')

        form = tk.Frame(top, bg=theme.CARD_BG)
        form.pack(fill='x', padx=14, pady=(0, 14))

        self._field(form, 0, 'Crop Name *', self.crop_name_var, self.crop_error)
        self._field(form, 1, 'Species *', self.species_var, self.species_error)

        btns = tk.Frame(form, bg=theme.CARD_BG)
        btns.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky='w')

        self.primary_button(
            btns,
            'Add Crop',
            self.add_crop,
            bg=theme.PRIMARY_LIGHT,
            width=12
        ).pack(side='left', padx=4)

        self.primary_button(
            btns,
            'Update Selected',
            self.update_crop,
            width=14
        ).pack(side='left', padx=4)

        self.primary_button(
            btns,
            'Delete Selected',
            self.delete_crop,
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

        table = self.section_card(self, 'Crop Records')
        table.pack(fill='both', expand=True, pady=(10, 0))

        holder = tk.Frame(table, bg=theme.CARD_BG)
        holder.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        cols = ('ID', 'Crop Name', 'Species', 'Created At')
        self.tree = ttk.Treeview(holder, columns=cols, show='headings', height=14)

        for col, width in zip(cols, [60, 160, 220, 160]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        sb = ttk.Scrollbar(holder, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

    def _field(self, parent, row, label, variable, error_var):
        tk.Label(
            parent,
            text=label,
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).grid(row=row, column=0, sticky='w', pady=6)

        tk.Entry(
            parent,
            textvariable=variable,
            width=32,
            font=theme.BODY_FONT,
            relief='solid',
            bd=1
        ).grid(row=row, column=1, padx=8, pady=6, ipady=5)

        tk.Label(
            parent,
            textvariable=error_var,
            bg=theme.CARD_BG,
            fg=theme.DANGER,
            font=theme.SMALL_FONT
        ).grid(row=row, column=2, sticky='w')

    def on_show(self):
        self.load_data()

    def validate_form(self):
        crop_error = validate_alpha_space(self.crop_name_var.get(), 'Crop name', min_len=2)
        species_error = validate_alpha_space(self.species_var.get(), 'Species', min_len=3, allow_dot=True)

        self.crop_error.set(crop_error)
        self.species_error.set(species_error)

        return not crop_error and not species_error

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in CropRepository.get_all():
            self.tree.insert(
                '',
                'end',
                values=(row['crop_id'], row['crop_name'], row['species'], str(row['created_at'])[:19])
            )

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        self.selected_id = values[0]
        self.crop_name_var.set(values[1])
        self.species_var.set(values[2])
        self.crop_error.set('')
        self.species_error.set('')

    def add_crop(self):
        if not self.validate_form():
            return

        CropRepository.insert(
            self.crop_name_var.get().strip(),
            self.species_var.get().strip()
        )

        self.clear_form()
        self.load_data()
        messagebox.showinfo('Success', 'Crop added successfully.')

    def update_crop(self):
        if not self.selected_id:
            messagebox.showwarning('Update', 'Select a crop row to update.')
            return

        if not self.validate_form():
            return

        CropRepository.update(
            int(self.selected_id),
            self.crop_name_var.get().strip(),
            self.species_var.get().strip()
        )

        self.clear_form()
        self.load_data()
        messagebox.showinfo('Updated', 'Crop updated successfully.')

    def delete_crop(self):
        if not self.selected_id:
            messagebox.showwarning('Delete', 'Select a crop row to delete.')
            return

        if messagebox.askyesno('Confirm Delete', 'Delete this crop record?'):
            CropRepository.delete(int(self.selected_id))
            self.clear_form()
            self.load_data()
            messagebox.showinfo('Deleted', 'Crop deleted successfully.')

    def clear_form(self):
        self.selected_id = None
        self.crop_name_var.set('')
        self.species_var.set('')
        self.crop_error.set('')
        self.species_error.set('')