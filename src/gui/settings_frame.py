from loguru import logger
import ttkbootstrap as tb
import tkinter as tk
from pathlib import Path

from ttkbootstrap.dialogs import Messagebox

from src.core.config import Config
from tkinter import filedialog
import shutil

class SettingsFrame(tb.Frame):
    def __init__(self, parent: tb.Frame, controller) -> None:
        super().__init__(parent, padding=10, borderwidth=1, relief="solid")
        self._controller = controller

        self._audio_file_path = tk.StringVar()
        self._volume = tk.DoubleVar()
        self._interval = tk.IntVar()
        self._volume_value_label = tb.Label()

        self.create_widgets()

    def create_widgets(self) -> None:
        sound_interval_frame = tb.Frame(self)
        sound_interval_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        sound_frame = tb.LabelFrame(sound_interval_frame, padding=10)
        sound_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        sound_interval_frame.grid_columnconfigure(0, weight=1)

        sound_label = tb.Label(sound_frame, text="File:")
        sound_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        sound_entry = tb.Entry(sound_frame, textvariable=self._audio_file_path, state="readonly", width=30)
        sound_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        browse_button = tb.Button(sound_frame, text="...", command=self._browse_audio_file, width=3)
        browse_button.grid(row=0, column=2, padx=5, pady=5)

        volume_label = tb.Label(sound_frame, text="Volume:")
        volume_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        volume_scale = tb.Scale(sound_frame, from_=0.0, to=1.0, variable=self._volume, command=self._on_volume_change, length=180)
        volume_scale.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        self._volume_value_label = tb.Label(sound_frame, text="50%", width=4, anchor="e")
        self._volume_value_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)

        sound_frame.columnconfigure(1, weight=1)

        interval_frame = tb.LabelFrame(sound_interval_frame, padding=10)
        interval_frame.grid(row=0, column=1, sticky="ns")

        interval_label = tb.Label(interval_frame, text="Interval (min)")
        interval_label.pack(pady=(0, 2))

        interval_spinbox = tb.Spinbox(interval_frame, from_=1, to=360, textvariable=self._interval, width=5, command=self._on_settings_change)
        interval_spinbox.pack()

        logger.info("SettingsFrame widgets created.")

    def _on_volume_change(self, value_str: str) -> None:
        try:
            value = float(value_str)
            vol_percent = int(value * 100)
            self._volume_value_label.config(text=f"{vol_percent}%")
            self._controller.request_update_settings({"volume": value})

        except ValueError:
            pass

    def _on_settings_change(self) -> None:
        settings = {
            "interval": self._interval.get(),
            "volume": self._volume.get(),
            "audio_file_path": self._audio_file_path.get()
        }

        self._controller.request_update_settings(settings)

    def update_settings(self, settings: dict) -> None:
        self._audio_file_path.set(settings.get("audio_file", Config.DEFAULT_SETTINGS["audio_file_path"]))
        self._volume.set(settings.get("volume", Config.DEFAULT_SETTINGS["volume"]))
        self._interval.set(settings.get("interval", Config.DEFAULT_SETTINGS["interval"]))
        self._volume_value_label.config(text=f"{int(self._volume.get() * 100)}%")

    def _browse_audio_file(self) -> None:
        try:
            initial_dir = Path(__file__).parent.parent.parent / "resources" / "audio"

            file_path = filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=[("Audio Files", "*.mp3"), ("All Files", "*.")],
                initialdir=initial_dir
            )

            if Path(file_path).exists():
                file_name = Path(file_path).name
                new_path = initial_dir / file_name

                if Path(file_path).resolve() != new_path.resolve():
                    shutil.copy2(file_path, new_path)

                self._audio_file_path.set(str(new_path))
                self._controller.request_update_settings({"audio_file_path": str(new_path)})

                logger.info("Audio file selected successfully")
        except Exception as e:
            logger.error(f"Failed to select audio file: {e}")
            Messagebox.show_error(message="Failed to select audio file", title="Error", parent=self)
