import os
import shutil

lagrange_default_config_path = "appsettings.json"
lagrange_config_path = "/app/data/appsettings.json"

os.makedirs(os.path.dirname(lagrange_config_path), exist_ok=True)
if not os.path.exists(lagrange_config_path):
    shutil.copyfile(lagrange_default_config_path, lagrange_config_path)
