import sounddevice as sd
import threading
from pathlib import Path
from .audio_player import AudioPlayer
from loguru import logger
from queue import Queue
from .config import Config

class DeviceMonitor:
    def __init__(self, request_queue: Queue, response_queue: Queue) -> None:
        self._thread = None
        self._stop_event = threading.Event()
        self.request_queue = request_queue
        self.response_queue = response_queue
        self._current_settings = Config.DEFAULT_SETTINGS.copy()

    def _update_settings(self) -> None:
        self.request_queue.put("GET_SETTINGS")
        logger.info("Waiting for settings...")

        try:
            self._current_settings.update(self.response_queue.get(timeout=5))
            logger.info("Settings received successfully")
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")

    def get_output_devices(self) -> list:
        try:
            devices = sd.query_devices()
            output_devices = list()

            for device in devices:
                if device["max_output_channels"] > 0:
                    output_devices.append(device["name"].lower().strip())

            return output_devices

        except Exception as e:
            logger.error(f"Failed to get output devices: {e}")
            return []

    def _is_target_device_connected(self) -> bool:
        connected_devices = self.get_output_devices()

        for target_device in self._current_settings["devices"]:
            for connected_device in connected_devices:
                if target_device == connected_device:
                    return True

        return False

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._update_settings()

                target_devices = self._current_settings.get("devices", Config.DEFAULT_SETTINGS["devices"])
                audio_file_path =self._current_settings.get("audio_file_path", Config.DEFAULT_SETTINGS["audio_file_path"])
                volume = self._current_settings.get("volume", Config.DEFAULT_SETTINGS["volume"])
                interval = self._current_settings.get("interval", Config.DEFAULT_SETTINGS["interval"])
                interval_seconds = interval * 60

                if not target_devices:
                    if self._stop_event.wait(15):
                        break

                    continue

                if not Path(audio_file_path).exists():
                    if self._stop_event.wait(15):
                        break

                    continue

                if self._is_target_device_connected():
                    AudioPlayer.play_audio(audio_file_path, volume)

                    if self._stop_event.wait(interval_seconds):
                        break
                else:
                    if self._stop_event.wait(15):
                        break

            except Exception as e:
                logger.error(f"Failed to monitor devices: {e}")

                if self._stop_event.wait(15):
                    break

        logger.info("Device monitoring stopped")
        self._thread = None

    def start(self) -> None:
        if self.is_running():
            logger.info("Device monitoring is already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop)
        self._thread.start()

        logger.info("Device monitoring started")

    def stop(self) -> None:
        if not self.is_running():
            logger.info("Device monitoring is not running")
            return

        self._stop_event.set()
        logger.info("Device monitoring stopped")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
