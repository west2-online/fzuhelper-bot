import os
import shutil
from pathlib import Path

LAGRANGE_DEFAULT_CONFIG_PATH = Path("appsettings.json")
LAGRANGE_CONFIG_PATH = Path("data/appsettings.json")
TEMP_DIR_PATH = Path("/app/data/temp")

os.makedirs(os.path.dirname(LAGRANGE_CONFIG_PATH), exist_ok=True)
if not os.path.exists(LAGRANGE_CONFIG_PATH):
    shutil.copyfile(LAGRANGE_DEFAULT_CONFIG_PATH, LAGRANGE_CONFIG_PATH)

os.makedirs(TEMP_DIR_PATH, exist_ok=True)