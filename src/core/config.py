from pathlib import Path
import json
from loguru import logger

class Config:
    SETTINGS_FILE_PATH = Path(__file__).parent.parent.parent / "resources" / "settings.json"
    DEFAULT_AUDIO_PATH = Path(__file__).parent.parent.parent / "resources" / "audio" / "default.mp3"
    DEFAULT_SETTINGS = {
        "devices": [],
        "audio_file_path": str(DEFAULT_AUDIO_PATH),
        "volume": 0.5,
        "interval": 5
    }

    @staticmethod
    def load_settings() -> dict:
        settings = Config.DEFAULT_SETTINGS.copy()

        if not Config.SETTINGS_FILE_PATH.exists():
            logger.error(f"Settings file not found: {Config.SETTINGS_FILE_PATH}")
            return settings

        try:
            with open(Config.SETTINGS_FILE_PATH, "r") as file:
                saved_settings = json.load(file)

                if saved_settings:
                    settings.update(saved_settings)

                logger.info("Settings loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

        return settings

    @staticmethod
    def save_settings(settings: dict) -> None:
        Config.SETTINGS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(Config.SETTINGS_FILE_PATH, "w") as file:
                json.dump(settings, file, indent=4)
                logger.info("Settings saved successfully")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
