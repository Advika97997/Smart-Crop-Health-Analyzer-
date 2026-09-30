from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from types import SimpleNamespace

from PIL import ImageTk

from config import theme
from core.validators import validate_notes, validate_required
from database.repositories import AnalysisRepository, CropRepository
from gui.base_page import BasePage
from services.analysis_service import AnalysisService
from services.export_service import ExportService
from services.image_service import ImageService


class HistoryPage(BasePage):
    page_title = 'Analysis History'
    page_subtitle = 'Filter by crop, review saved records, update crop and notes, and preview images.'

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.search_var = tk.StringVar()
        self.crop_filter_var = tk.StringVar(value='All Crops')
        self.edit_crop_var = tk.StringVar()

        self.selected_result_id = None
        self.current_record = None
        self.crop_map = {}

        self.original_photo = None
        self.processed_photo = None

        self.status_var = tk.StringVar(value='Health Status: —')
        self.score_var = tk.StringVar(value='Health Score: —')
        self.green_var = tk.StringVar(value='Green Coverage: —')
        self.disease_var = tk.StringVar(value='Disease Region: —')
        self.edge_var = tk.StringVar(value='Edge Density: —')
        self.advice_var = tk.StringVar(value='Advice: —')
        self.date_var = tk.StringVar(value='Analyzed On: —')

        self.build_page_header()
        self._build_ui()

    def _build_ui(self):
        top = self.section_card(self, 'History Controls')
        top.pack(fill='x')

        controls = tk.Frame(top, bg=theme.CARD_BG)
        controls.pack(fill='x', padx=12, pady=(0, 12))

        tk.Label(
            controls,
            text='Search',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).pack(side='left')

        search_entry = tk.Entry(
            controls,
            textvariable=self.search_var,
            width=18,
            font=theme.BODY_FONT,
            relief='solid',
            bd=1
        )
        search_entry.pack(side='left', padx=(6, 10), ipady=4)
        search_entry.bind('<Return>', lambda _e: self.refresh())

        tk.Label(
            controls,
            text='Crop Filter',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).pack(side='left')

        self.crop_filter_box = ttk.Combobox(
            controls,
            textvariable=self.crop_filter_var,
            state='readonly',
            width=16
        )
        self.crop_filter_box.pack(side='left', padx=(6, 10))
        self.crop_filter_box.bind('<<ComboboxSelected>>', lambda _e: self.refresh())

        self.primary_button(
            controls,
            'Refresh',
            self.refresh,
            bg=theme.PRIMARY_LIGHT,
            width=10
        ).pack(side='left', padx=3)

        self.primary_button(
            controls,
            'Save Changes',
            self.save_changes,
            width=12
        ).pack(side='left', padx=3)

        self.primary_button(
            controls,
            'Delete',
            self.delete_selected,
            bg=theme.DANGER,
            width=10
        ).pack(side='left', padx=3)

        self.primary_button(
            controls,
            'Export CSV',
            self.export_csv,
            width=10
        ).pack(side='right', padx=3)

        self.primary_button(
            controls,
            'Export PDF',
            self.export_pdf,
            bg=theme.PRIMARY_LIGHT,
            width=10
        ).pack(side='right', padx=3)

        body = tk.Frame(self, bg=theme.BG_APP)
        body.pack(fill='both', expand=True, pady=(8, 0))

        # Left: records table
        left = self.section_card(body, 'Saved Records')
        left.pack(side='left', fill='both', expand=True, padx=(0, 8))

        left_holder = tk.Frame(left, bg=theme.CARD_BG)
        left_holder.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        cols = ('ID', 'Crop', 'Status', 'Score', 'Analyzed On')
        self.tree = ttk.Treeview(left_holder, columns=cols, show='headings', height=13)

        for col, width in zip(cols, [55, 120, 110, 80, 150]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        sb = ttk.Scrollbar(left_holder, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        # Right: scrollable details
        right = self.section_card(body, 'Selected Record')
        right.pack(side='left', fill='both', padx=(8, 0))
        right.configure(width=520)
        right.pack_propagate(False)

        right_container = tk.Frame(right, bg=theme.CARD_BG)
        right_container.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        self.detail_canvas = tk.Canvas(
            right_container,
            bg=theme.CARD_BG,
            highlightthickness=0
        )
        self.detail_canvas.pack(side='left', fill='both', expand=True)

        detail_scrollbar = ttk.Scrollbar(
            right_container,
            orient='vertical',
            command=self.detail_canvas.yview
        )
        detail_scrollbar.pack(side='right', fill='y')

        self.detail_canvas.configure(yscrollcommand=detail_scrollbar.set)

        self.detail_frame = tk.Frame(self.detail_canvas, bg=theme.CARD_BG)
        self.detail_window = self.detail_canvas.create_window(
            (0, 0),
            window=self.detail_frame,
            anchor='nw'
        )

        self.detail_frame.bind('<Configure>', self._on_detail_configure)
        self.detail_canvas.bind('<Configure>', self._on_canvas_configure)

        # Editable crop row
        edit_row = tk.Frame(self.detail_frame, bg=theme.CARD_BG)
        edit_row.pack(fill='x', pady=(0, 8))

        tk.Label(
            edit_row,
            text='Crop',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).pack(side='left')

        self.edit_crop_box = ttk.Combobox(
            edit_row,
            textvariable=self.edit_crop_var,
            state='readonly',
            width=18
        )
        self.edit_crop_box.pack(side='left', padx=(8, 0))

        # Image row
        images_row = tk.Frame(self.detail_frame, bg=theme.CARD_BG)
        images_row.pack(fill='x', pady=(2, 8))

        img_left = tk.Frame(images_row, bg=theme.CARD_BG)
        img_left.pack(side='left', fill='x', expand=True, padx=(0, 6))

        tk.Label(
            img_left,
            text='Original',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.HEADER_FONT
        ).pack(anchor='w', pady=(0, 4))

        self.original_label = tk.Label(
            img_left,
            text='Select a row',
            bg='#f1f7f3',
            fg=theme.MUTED,
            font=theme.BODY_FONT,
            bd=1,
            relief='solid'
        )
        self.original_label.pack(fill='x', pady=(0, 4))

        img_right = tk.Frame(images_row, bg=theme.CARD_BG)
        img_right.pack(side='left', fill='x', expand=True, padx=(6, 0))

        tk.Label(
            img_right,
            text='Processed',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.HEADER_FONT
        ).pack(anchor='w', pady=(0, 4))

        self.processed_label = tk.Label(
            img_right,
            text='Preview',
            bg='#f1f7f3',
            fg=theme.MUTED,
            font=theme.BODY_FONT,
            bd=1,
            relief='solid'
        )
        self.processed_label.pack(fill='x', pady=(0, 4))

        # Metrics
        info_box = tk.Frame(self.detail_frame, bg='#f6fbf7', bd=1, relief='solid')
        info_box.pack(fill='x', pady=(4, 8))

        for var in [
            self.status_var,
            self.score_var,
            self.green_var,
            self.disease_var,
            self.edge_var,
            self.advice_var,
            self.date_var,
        ]:
            tk.Label(
                info_box,
                textvariable=var,
                bg='#f6fbf7',
                fg=theme.TEXT if var != self.advice_var else theme.MUTED,
                anchor='w',
                justify='left',
                wraplength=450,
                font=theme.BODY_FONT
            ).pack(fill='x', padx=8, pady=3)

        # Notes
        tk.Label(
            self.detail_frame,
            text='Notes',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.HEADER_FONT
        ).pack(anchor='w', pady=(2, 4))

        self.notes_text = tk.Text(
            self.detail_frame,
            height=5,
            font=theme.BODY_FONT,
            relief='solid',
            bd=1
        )
        self.notes_text.pack(fill='x')

        self.primary_button(
            self.detail_frame,
            'Save Changes',
            self.save_changes,
            width=14
        ).pack(anchor='e', pady=(8, 0))

        self._bind_detail_mousewheel()

    def _on_detail_configure(self, _event=None):
        self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        self.detail_canvas.itemconfigure(self.detail_window, width=event.width)

    def _bind_detail_mousewheel(self):
        self.detail_canvas.bind('<Enter>', self._enable_mousewheel)
        self.detail_canvas.bind('<Leave>', self._disable_mousewheel)
        self.detail_frame.bind('<Enter>', self._enable_mousewheel)
        self.detail_frame.bind('<Leave>', self._disable_mousewheel)

    def _enable_mousewheel(self, _event=None):
        self.detail_canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _disable_mousewheel(self, _event=None):
        self.detail_canvas.unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event):
        self.detail_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def on_show(self):
        self.crop_map = CropRepository.get_name_map()
        crop_names = ['All Crops'] + list(self.crop_map.keys())
        self.crop_filter_box['values'] = crop_names
        self.edit_crop_box['values'] = list(self.crop_map.keys())

        if not self.crop_filter_var.get():
            self.crop_filter_var.set('All Crops')

        self.refresh()

    def _records(self):
        crop_filter = self.crop_filter_var.get().strip()
        if crop_filter == 'All Crops':
            crop_filter = ''

        return AnalysisRepository.get_all(
            filter_text=self.search_var.get().strip(),
            crop_name=crop_filter
        )

    def refresh(self):
        records = self._records()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in records:
            self.tree.insert('', 'end', values=(
                row['result_id'],
                row['crop_name'],
                row['health_status'],
                row['health_score'],
                str(row['analyzed_on'])[:19],
            ))

        self.controller.set_status(f'{len(records)} history record(s) loaded.')

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return

        result_id = int(self.tree.item(selected[0])['values'][0])
        self.load_details(result_id)

    def load_details(self, result_id: int):
        record = AnalysisRepository.get_one(result_id)
        if not record:
            messagebox.showwarning('History', 'Could not load selected record.')
            return

        self.selected_result_id = result_id
        self.current_record = record

        self.edit_crop_var.set(record['crop_name'])

        self.notes_text.delete('1.0', 'end')
        self.notes_text.insert('1.0', record.get('notes') or '')

        self.status_var.set(f"Health Status: {record['health_status']}")
        self.score_var.set(f"Health Score: {record['health_score']}")
        self.green_var.set(f"Green Coverage: {record['green_percentage']}%")
        self.disease_var.set(f"Disease Region: {record['disease_area_percentage']}%")
        self.edge_var.set(f"Edge Density: {record['edge_density']}%")
        self.advice_var.set(f"Advice: {record.get('advice') or '—'}")
        self.date_var.set(f"Analyzed On: {str(record['analyzed_on'])[:19]}")

        self._load_images(record['image_path'])
        self.detail_canvas.yview_moveto(0)

        self.controller.set_status(f'Record {result_id} loaded.')

    def _load_images(self, image_path: str):
        try:
            original_pil = ImageService.load_image(image_path, size=(210, 140))
            processed_pil = ImageService.process_for_view(original_pil, 'Disease Highlight')

            self.original_photo = ImageTk.PhotoImage(original_pil)
            self.processed_photo = ImageTk.PhotoImage(processed_pil)

            self.original_label.configure(image=self.original_photo, text='')
            self.processed_label.configure(image=self.processed_photo, text='')
        except Exception:
            self.original_photo = None
            self.processed_photo = None
            self.original_label.configure(image='', text='Image unavailable')
            self.processed_label.configure(image='', text='Preview unavailable')

    def save_changes(self):
        if not self.selected_result_id or not self.current_record:
            messagebox.showwarning('Update', 'Select a history record first.')
            return

        error = validate_required(self.edit_crop_var.get(), 'Crop')
        error = error or validate_notes(self.notes_text.get('1.0', 'end').strip())
        if error:
            messagebox.showwarning('Validation', error)
            return

        crop_name = self.edit_crop_var.get().strip()
        crop_id = self.crop_map[crop_name]
        notes = self.notes_text.get('1.0', 'end').strip()

        metrics = SimpleNamespace(
            status=self.current_record['health_status'],
            health_score=self.current_record['health_score'],
            green_pct=self.current_record['green_percentage'],
            disease_pct=self.current_record['disease_area_percentage'],
            edge_density=self.current_record['edge_density'],
        )

        advice = AnalysisService.get_advice(crop_name, metrics)

        ok = AnalysisRepository.update_record(
            result_id=self.selected_result_id,
            crop_id=crop_id,
            notes=notes,
            advice=advice,
        )

        if not ok:
            messagebox.showerror('Update', 'Failed to update selected record.')
            return

        messagebox.showinfo('Updated', 'Record updated successfully.')
        self.refresh()
        self.load_details(self.selected_result_id)

    def delete_selected(self):
        if not self.selected_result_id:
            messagebox.showwarning('Delete', 'Select a row to delete.')
            return

        if messagebox.askyesno('Confirm Delete', 'Delete the selected history record?'):
            AnalysisRepository.delete(self.selected_result_id)
            self.selected_result_id = None
            self.current_record = None
            self.refresh()
            self._clear_details()
            messagebox.showinfo('Deleted', 'Record deleted successfully.')

    def export_csv(self):
        records = self._records()
        if not records:
            messagebox.showwarning('Export', 'No records available to export.')
            return

        path = ExportService.export_csv(records)
        self.controller.set_status(f'CSV exported to {path}')
        messagebox.showinfo('Export Complete', f'CSV exported successfully.\n\n{path}')

    def export_pdf(self):
        records = self._records()
        if not records:
            messagebox.showwarning('Export', 'No records available to export.')
            return

        path = ExportService.export_pdf(records)
        self.controller.set_status(f'PDF exported to {path}')
        messagebox.showinfo('Export Complete', f'PDF exported successfully.\n\n{path}')

    def _clear_details(self):
        self.edit_crop_var.set('')
        self.notes_text.delete('1.0', 'end')

        self.status_var.set('Health Status: —')
        self.score_var.set('Health Score: —')
        self.green_var.set('Green Coverage: —')
        self.disease_var.set('Disease Region: —')
        self.edge_var.set('Edge Density: —')
        self.advice_var.set('Advice: —')
        self.date_var.set('Analyzed On: —')

        self.original_photo = None
        self.processed_photo = None
        self.original_label.configure(image='', text='Select a row')
        self.processed_label.configure(image='', text='Preview')