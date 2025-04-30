import json
import os
import sys

SETTINGS_FILENAME = "settings.json"
DEFAULT_SOUND_FILENAME = "default.mp3"

try:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    SETTINGS_FILE_PATH = os.path.join(app_dir, SETTINGS_FILENAME)
except NameError:
    app_dir = os.getcwd()
    SETTINGS_FILE_PATH = os.path.join(app_dir, SETTINGS_FILENAME)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
DEFAULT_SOUND_FILE_PATH = os.path.join(ASSETS_DIR, DEFAULT_SOUND_FILENAME)

DEFAULT_SETTINGS = {
    "headsets": [],
    "sound_file": DEFAULT_SOUND_FILE_PATH,
    "volume": 0.5,
    "interval_minutes": 5
}

def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    
    try:
        if os.path.exists(SETTINGS_FILE_PATH):
            with open(SETTINGS_FILE_PATH, "r") as file:
                loaded_settings = dict(json.load(file))
                
                for key in DEFAULT_SETTINGS.keys():
                    if key in loaded_settings.keys():
                        if key == "sound_file":
                            if os.path.exists(loaded_settings[key]):
                                settings[key] = os.path.abspath(load_settings[key])
                            else:
                                print(f"WARNING: Sound file {loaded_settings[key]} does not exist")
                                settings[key] = DEFAULT_SETTINGS[key]
                        elif key == "volume":
                            try:
                                volume = float(load_settings[key])
                                settings[key] = max(0.0, min(volume, 1.0))
                            except (ValueError, TypeError):
                                print(f"WARNING: Invalid volume {loaded_settings[key]}")
                                settings[key] = DEFAULT_SETTINGS[key]
                        elif key == "interval_minutes":
                            try:
                                interval = int(loaded_settings[key])
                                settings[key] = max(1, min(interval, 60))
                            except (ValueError, TypeError):
                                print(f"WARNING: Invalid interval (minutes) {loaded_settings[key]}")
                                settings[key] = DEFAULT_SETTINGS[key]
                        elif key == "headsets":
                            try:
                                headsets = [str(item) for item in loaded_settings[key]]
                                settings[key] = headsets
                            except (ValueError, TypeError):
                                print(f"WARNING: Invalid headsets {loaded_settings[key]}")
                                settings[key] = DEFAULT_SETTINGS[key]
                    
            print(f"INFO: Loaded settings from {SETTINGS_FILE_PATH}")
        else:
            print(f"INFO: No settings file found at {SETTINGS_FILE_PATH}")
    except Exception:
        print(f"WARNING: Failed to load settings from {SETTINGS_FILE_PATH}")
    
    return settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE_PATH, "w") as file:
            json.dump(settings, file)
        
        print(f"INFO: Saved settings to {SETTINGS_FILE_PATH}")
        return True
    except Exception:
        print(f"WARNING: Failed to save settings to {SETTINGS_FILE_PATH}")
        return False
