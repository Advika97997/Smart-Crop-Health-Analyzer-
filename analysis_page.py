from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import ImageTk

from config import settings, theme
from core.helpers import normalize_path
from core.validators import validate_image_file, validate_notes, validate_required
from database.repositories import AnalysisRepository, CropRepository
from gui.base_page import BasePage
from services.analysis_service import AnalysisService
from services.image_service import ImageService


class AnalysisPage(BasePage):
    page_title = 'Upload & Analysis'
    page_subtitle = 'Upload a crop image, process it with computer vision, and save the result.'

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.image_path = ''
        self.crop_map = {}
        self.current_metrics = None
        self.original_photo = None
        self.processed_photo = None

        self.crop_var = tk.StringVar()
        self.view_var = tk.StringVar(value='Enhanced')

        self.health_var = tk.StringVar(value='Health Status: —')
        self.score_var = tk.StringVar(value='Health Score: —')
        self.green_var = tk.StringVar(value='Green Coverage: —%')
        self.disease_var = tk.StringVar(value='Disease Region: —%')
        self.edge_var = tk.StringVar(value='Edge Density: —%')
        self.advice_var = tk.StringVar(value='Advice: —')

        self.file_var = tk.StringVar(value='No image selected')
        self.loading_var = tk.StringVar(value='Idle')

        self.build_page_header()
        self._build_ui()

    def _build_ui(self):
        top = self.section_card(self, 'Analysis Workspace')
        top.pack(fill='x')

        controls = tk.Frame(top, bg=theme.CARD_BG)
        controls.pack(fill='x', padx=14, pady=(0, 14))

        self.primary_button(
            controls,
            'Upload Image',
            self.upload_image,
            bg=theme.PRIMARY_LIGHT,
            width=14
        ).pack(side='left', padx=(0, 8))

        tk.Label(
            controls,
            textvariable=self.file_var,
            bg=theme.CARD_BG,
            fg=theme.MUTED,
            font=theme.SMALL_FONT
        ).pack(side='left', padx=(0, 14))

        tk.Label(
            controls,
            text='Crop',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).pack(side='left')

        self.crop_box = ttk.Combobox(
            controls,
            textvariable=self.crop_var,
            state='readonly',
            width=12
        )
        self.crop_box.pack(side='left', padx=6)

        tk.Label(
            controls,
            text='View',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).pack(side='left', padx=(10, 0))

        self.view_box = ttk.Combobox(
            controls,
            textvariable=self.view_var,
            state='readonly',
            width=15,
            values=list(ImageService.VIEW_MODES.keys())
        )
        self.view_box.pack(side='left', padx=6)

        self.primary_button(
            controls,
            'Process',
            self.process_image,
            width=12
        ).pack(side='left', padx=10)

        self.primary_button(
            controls,
            'Save to Database',
            self.save_result,
            bg=theme.PRIMARY_LIGHT,
            width=16
        ).pack(side='left', padx=8)

        tk.Label(
            controls,
            textvariable=self.loading_var,
            bg=theme.CARD_BG,
            fg=theme.INFO,
            font=theme.SMALL_FONT
        ).pack(side='left', padx=8)

        center = tk.Frame(self, bg=theme.BG_APP)
        center.pack(fill='both', expand=True, pady=(8, 8))

        left = self.section_card(center, 'Original Image')
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.original_label = tk.Label(
            left,
            text='Upload an image to preview here',
            bg='#f1f7f3',
            fg=theme.MUTED,
            font=theme.BODY_FONT,
            height=12
        )
        self.original_label.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        right = self.section_card(center, 'Processed Output')
        right.pack(side='left', fill='both', expand=True)

        self.processed_label = tk.Label(
            right,
            text='Processed image will appear here',
            bg='#f1f7f3',
            fg=theme.MUTED,
            font=theme.BODY_FONT,
            height=12
        )
        self.processed_label.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        bottom = tk.Frame(self, bg=theme.BG_APP)
        bottom.pack(fill='x', pady=(0, 6))

        stats = self.section_card(bottom, 'Analysis Insights')
        stats.pack(side='left', fill='both', expand=True, padx=(0, 10))

        stats_inner = tk.Frame(stats, bg=theme.CARD_BG)
        stats_inner.pack(fill='both', expand=True, padx=14, pady=(0, 12))

        for var in [
            self.health_var,
            self.score_var,
            self.green_var,
            self.disease_var,
            self.edge_var,
            self.advice_var
        ]:
            tk.Label(
                stats_inner,
                textvariable=var,
                bg=theme.CARD_BG,
                fg=theme.TEXT if var != self.advice_var else theme.MUTED,
                justify='left',
                anchor='w',
                wraplength=380,
                font=theme.BODY_FONT
            ).pack(fill='x', pady=3)

        notes_card = self.section_card(bottom, 'Save Analysis')
        notes_card.pack(side='left', fill='both', expand=True)

        notes_inner = tk.Frame(notes_card, bg=theme.CARD_BG)
        notes_inner.pack(fill='both', expand=True, padx=14, pady=(0, 12))

        tk.Label(
            notes_inner,
            text='Notes',
            bg=theme.CARD_BG,
            fg=theme.TEXT,
            font=theme.BODY_FONT
        ).pack(anchor='w')

        self.notes_text = tk.Text(
            notes_inner,
            height=4,
            font=theme.BODY_FONT,
            relief='solid',
            bd=1
        )
        self.notes_text.pack(fill='x', pady=(6, 8))

        self.primary_button(
            notes_inner,
            'Save to Database',
            self.save_result,
            width=18
        ).pack(anchor='e')

    def on_show(self):
        self.crop_map = CropRepository.get_name_map()
        self.crop_box['values'] = list(self.crop_map.keys())
        if self.crop_map and not self.crop_var.get():
            self.crop_var.set(next(iter(self.crop_map.keys())))

    def upload_image(self):
        path = filedialog.askopenfilename(
            title='Choose crop image',
            filetypes=settings.SUPPORTED_IMAGE_TYPES
        )
        if not path:
            return

        self.image_path = normalize_path(path)
        self.file_var.set(Path(self.image_path).name)

        pil = ImageService.load_image(self.image_path, size=(300, 220))
        self.original_photo = ImageTk.PhotoImage(pil)
        self.original_label.configure(image=self.original_photo, text='')

        self.processed_label.configure(image='', text='Processed image will appear here')
        self.processed_photo = None
        self.current_metrics = None
        self._reset_metrics()

        self.loading_var.set('Image loaded')
        self.controller.set_status(f'Loaded image: {self.image_path}')

    def process_image(self):
        validation_error = validate_image_file(self.image_path) or validate_required(self.crop_var.get(), 'Crop')
        if validation_error:
            messagebox.showwarning('Validation', validation_error)
            return

        self.loading_var.set('Processing...')
        self.update_idletasks()

        original = ImageService.load_image(self.image_path, size=(300, 220))
        processed = ImageService.process_for_view(original, self.view_var.get())
        metrics = ImageService.compute_metrics(original)

        self.current_metrics = metrics
        self.processed_photo = ImageTk.PhotoImage(processed)
        self.processed_label.configure(image=self.processed_photo, text='')

        advice = AnalysisService.get_advice(self.crop_var.get(), metrics)
        self.health_var.set(f'Health Status: {metrics.status}')
        self.score_var.set(f'Health Score: {metrics.health_score}/100')
        self.green_var.set(f'Green Coverage: {metrics.green_pct}%')
        self.disease_var.set(f'Disease Region: {metrics.disease_pct}%')
        self.edge_var.set(f'Edge Density: {metrics.edge_density}%')
        self.advice_var.set(f'Advice: {advice}')

        self.loading_var.set('Completed')
        self.controller.set_status('Image processed successfully.')

    def save_result(self):
        validation_error = validate_image_file(self.image_path)
        validation_error = validation_error or validate_required(self.crop_var.get(), 'Crop')
        validation_error = validation_error or ('' if self.current_metrics else 'Process the image before saving.')
        validation_error = validation_error or validate_notes(self.notes_text.get('1.0', 'end').strip())

        if validation_error:
            messagebox.showwarning('Validation', validation_error)
            return

        crop_id = self.crop_map[self.crop_var.get()]
        notes = self.notes_text.get('1.0', 'end').strip()
        advice = AnalysisService.get_advice(self.crop_var.get(), self.current_metrics)

        image_id = AnalysisRepository.save_image(crop_id, self.image_path)
        AnalysisRepository.save_result(
            image_id=image_id,
            health_status=self.current_metrics.status,
            health_score=self.current_metrics.health_score,
            green_pct=self.current_metrics.green_pct,
            disease_pct=self.current_metrics.disease_pct,
            edge_density=self.current_metrics.edge_density,
            advice=advice,
            notes=notes,
        )

        messagebox.showinfo('Saved', 'Analysis result saved successfully.')
        self.notes_text.delete('1.0', 'end')
        self.loading_var.set('Saved')
        self.controller.set_status('Analysis saved to database.')

    def _reset_metrics(self):
        self.health_var.set('Health Status: —')
        self.score_var.set('Health Score: —')
        self.green_var.set('Green Coverage: —%')
        self.disease_var.set('Disease Region: —%')
        self.edge_var.set('Edge Density: —%')
        self.advice_var.set('Advice: —')