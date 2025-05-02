import queue
from queue import Queue
from pathlib import Path
import ttkbootstrap as tb
from loguru import logger
from ttkbootstrap.dialogs import Messagebox
from ..core.config import Config
from ..core.device_monitor import DeviceMonitor
from .head_set_frame import HeadsetFrame
from .settings_frame import SettingsFrame
from .control_frame import ControlFrame


class App(tb.Window):
    def __init__(self) -> None:
        super().__init__(title="KeepAlive", themename="darkly")
        self.geometry("750x450")
        self._set_icon()

        self._current_settings = dict()
        self._available_devices = list()

        self._monitor_request_queue = Queue()
        self._monitor_response_queue = Queue()
        self._device_monitor = DeviceMonitor(self._monitor_request_queue, self._monitor_response_queue)

        self._create_widgets()
        self._load_initial_data()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._process_monitor_requests)
        self.after(6000, self._schedule_device_refresh)

        logger.info("Main window created successfully")

    def _set_icon(self) -> None:
        try:
            icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "icon.ico"

            if icon_path.exists():
                self.iconbitmap(str(icon_path))
                logger.info("Icon set successfully")
            else:
                logger.error(f"Icon file not found: {icon_path}")

        except Exception as e:
            logger.error(f"Failed to set icon: {e}")

    def _create_widgets(self) -> None:
        container = tb.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        self.headset_frame = HeadsetFrame(container, self)
        self.headset_frame.pack(fill="x", pady=(0, 10))

        self.settings_frame = SettingsFrame(container, self)
        self.settings_frame.pack(fill="x", pady=(0, 10))

        self.control_frame = ControlFrame(container, self)
        self.control_frame.pack(fill="x", pady=(0, 10))

    def _process_monitor_requests(self) -> None:
        try:
            message = self._monitor_request_queue.get_nowait()

            if message == "GET_SETTINGS":
                self._monitor_response_queue.put(self._current_settings.copy())
                logger.info("Settings sent successfully")

        except queue.Empty:
            pass

        except Exception as e:
            logger.error(f"Failed to process monitor requests: {e}")

        if self.winfo_exists():
            self.after(100, self._process_monitor_requests)

    def _schedule_device_refresh(self):
        self._refresh_available_devices()
        self.after(60000, self._schedule_device_refresh)

    def _load_initial_data(self) -> None:
        logger.info("Displaying initial data...")

        self._current_settings = Config.load_settings()
        self.headset_frame.update_list(self._current_settings.get("devices", Config.DEFAULT_SETTINGS["devices"]))
        self.settings_frame.update_settings(self._current_settings)
        self._refresh_available_devices()

    def _refresh_available_devices(self) -> None:
        try:
            self._available_devices = self._device_monitor.get_output_devices()
            self.headset_frame.update_available_devices(self._available_devices)

            logger.info("Available devices refreshed successfully")
        except Exception as e:
            logger.error(f"Failed to refresh available devices: {e}")
            self.headset_frame.update_available_devices(list())

    def _on_close(self) -> None:
        if self._device_monitor.is_running():
            self._device_monitor.stop()

        Config.save_settings(self._current_settings)
        self.destroy()

        logger.info("Main window closed successfully")

    def request_add_headset(self, headset_name: str) -> None:
        try:
            if headset_name not in self._current_settings.get("devices", []):
                self._current_settings["devices"].append(headset_name)
                self.headset_frame.update_list(self._current_settings.get("devices", []))

                Config.save_settings(self._current_settings)
                self._refresh_available_devices()
                logger.info("Headset added successfully")

        except Exception as e:
            logger.error(f"Failed to add headset: {e}")
            Messagebox.show_error(message="Failed to add headset", title="Error", parent=self)

    def request_remove_headset(self, headset_name: str) -> None:
        try:
            self._current_settings["devices"].remove(headset_name)
            self.headset_frame.update_list(self._current_settings.get("devices", []))

            Config.save_settings(self._current_settings)
            self._refresh_available_devices()
            logger.info("Headset removed successfully")

        except ValueError:
            logger.info("Headset already removed")

        except Exception as e:
            logger.error(f"Failed to remove headset: {e}")
            Messagebox.show_error(message="Failed to remove headset", title="Error", parent=self)

    def request_update_settings(self, settings: dict) -> None:
        try:
            self._current_settings.update(settings)
            Config.save_settings(self._current_settings)
            logger.info("Settings updated successfully")

        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            Messagebox.show_error(message="Failed to update settings", title="Error", parent=self)

    def start_monitor(self) -> None:
        if self._device_monitor.is_running():
            self.control_frame.update_status("Monitoring devices...")
            logger.info("Device monitor already running")
            return

        if not self._current_settings.get("devices", []):
            Messagebox.show_warning(message="Please add at least one device to monitor", title="Warning", parent=self)
            logger.info("No devices to monitor")
            return

        if not Path(self._current_settings.get("audio_path", "")).exists():
            Messagebox.show_warning(message="Please select an audio file", title="Warning", parent=self)
            logger.info("No audio file selected")
            return

        self._device_monitor.start()
        self.control_frame.update_status("Monitoring devices...")
        logger.info("Device monitor started successfully")

    def stop_monitor(self) -> None:
        if not self._device_monitor.is_running():
            self.control_frame.update_status("Device monitor stopped...")
            logger.info("Device monitor not running")
            return

        self._device_monitor.stop()
        self.control_frame.update_status("Device monitor stopped...")
        logger.info("Device monitor stopped successfully")
