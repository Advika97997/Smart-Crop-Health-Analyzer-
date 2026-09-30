# Crop Health Analyzer – Image-Based Farming Solution

## 1. Project Overview

**Crop Health Analyzer** is a desktop-based agriculture support system developed using **Python, Tkinter, MySQL, OpenCV, Pillow, and ReportLab**. The application helps users upload crop images, analyze plant health using image processing techniques, store the results in a database, and review previous analyses through a dashboard and history module.

The main goal of the project is to provide a simple and practical **image-based crop monitoring solution** that can support farmers, agricultural researchers, and students in understanding crop condition using digital tools.

This project was designed as a **micro project / academic project**, but the code structure, modules, and features were organized in a more professional way so that it resembles a small production-style desktop application.

---

## 2. Problem Statement

In traditional farming, crop health is often assessed manually by visual observation. This can be:

- time-consuming
- inconsistent
- experience-dependent
- difficult to track over time

This project addresses that problem by allowing a user to:

- upload a crop image
- process the image using computer vision
- estimate crop health condition
- generate a health score
- provide basic crop advice
- save the result for future reference

---

## 3. Objectives

The major objectives of this project are:

- to build a multi-page desktop application using Python
- to integrate a relational database using MySQL
- to perform image-based crop analysis using OpenCV and Pillow
- to implement CRUD operations for crop and farmer management
- to provide a history and dashboard system
- to generate exportable reports in CSV and PDF format
- to satisfy academic rubric requirements while maintaining modular design

---

## 4. Key Features

### Core Features
- Login system
- Dashboard with analytics
- Crop image upload and analysis
- Health score generation
- Health classification
- Smart crop advice
- MySQL database integration
- Crop management with CRUD
- Farmer management with CRUD
- Analysis history view
- Search and crop-based filtering in history
- Update crop and notes in history
- Delete saved analysis records
- Export history to CSV
- Export history to PDF

### Innovative Features
- Image-based health score engine
- Disease highlight view
- Dashboard analytics with bar charts
- History preview with original and processed images
- Smart advice generation based on crop health condition

---

## 5. Technology Stack

| Technology | Purpose |
|-----------|---------|
| Python | Main programming language |
| Tkinter | Desktop user interface |
| MySQL | Database storage |
| OpenCV | Image processing and computer vision |
| Pillow (PIL) | Image loading, resizing, Tkinter image support |
| NumPy | Pixel and array manipulation |
| ReportLab | PDF export generation |

---

## 6. Why These Technologies Were Chosen

### Python
Python is simple, readable, and ideal for rapid application development. It also has strong support for image processing and GUI development.

### Tkinter
Tkinter is built into Python and is suitable for academic desktop projects. It is lightweight and easy to integrate with Python logic.

### MySQL
MySQL is a powerful relational database system. It is widely used in industry and suitable for structured data such as users, crops, farmers, images, and analysis records.

### OpenCV
OpenCV is used for computer vision tasks such as color masking, image conversion, and edge detection.

### Pillow
Pillow is used to load and resize images so they can be displayed in the Tkinter interface.

### ReportLab
ReportLab is used for generating PDF reports from saved records.

---

## 7. Project Architecture

The project follows a **layered modular architecture**, which separates UI, business logic, database access, and configuration.

```text
crop_health_analyzer_pro/
│
├── main.py
├── requirements.txt
├── README.md
├── schema.sql
│
├── config/
│   ├── settings.py
│   └── theme.py
│
├── core/
│   ├── app_controller.py
│   ├── navigation.py
│   ├── validators.py
│   └── helpers.py
│
├── database/
│   ├── db.py
│   ├── repositories.py
│   └── seed.py
│
├── services/
│   ├── image_service.py
│   ├── analysis_service.py
│   ├── dashboard_service.py
│   └── export_service.py
│
├── gui/
│   ├── base_page.py
│   ├── login_page.py
│   ├── dashboard_page.py
│   ├── analysis_page.py
│   ├── history_page.py
│   ├── crops_page.py
│   └── farmer_page.py
│
└── exports/