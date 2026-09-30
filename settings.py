from __future__ import annotations

import os
from pathlib import Path

APP_TITLE = 'Crop Health Analyzer – Image-Based Farming Solution'
APP_GEOMETRY = '1366x820'
APP_MIN_SIZE = (1200, 760)
BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / 'exports'
EXPORT_DIR.mkdir(exist_ok=True)

DB_CONFIG = {
    'host': os.getenv('CHA_DB_HOST', 'localhost'),
    'user': os.getenv('CHA_DB_USER', 'root'),
    'password': os.getenv('CHA_DB_PASSWORD', 'Alan@mysq1'),#change the password
    'database': os.getenv('CHA_DB_NAME', 'crop_health_db'),
}

SUPPORTED_IMAGE_TYPES = [('Image Files', '*.png *.jpg *.jpeg *.bmp')]
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD_HINT = 'admin123'

SIDEBAR_ITEMS = [
    ('Dashboard', 'DashboardPage'),
    ('Analysis', 'AnalysisPage'),
    ('History', 'HistoryPage'),
    ('Manage Crops', 'CropsPage'),
    ('Farmers', 'FarmerPage'),
]
