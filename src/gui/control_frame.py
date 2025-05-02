import ttkbootstrap as tb
from loguru import logger

class ControlFrame(tb.Frame):
    def __init__(self, parent: tb.Frame, controller) -> None:
        super().__init__(parent)
        self.controller = controller

        self._create_widgets()

    def _create_widgets(self) -> None:
        button_frame = tb.Frame(self)
        button_frame.pack(side="left", fill="y", padx=(5, 0), expand=True)

        self._status = tb.StringVar(value="Waiting...")
        self._status_label = tb.Label(button_frame, textvariable=self._status, anchor="center", justify="center", width=30, relief="solid", padding=5)
        self._status_label.pack(side="top", pady=10)

        start_monitor_button = tb.Button(button_frame, text="Start", command=self.controller.start_monitor, width=30)
        start_monitor_button.pack(side="top", pady=5)

        stop_monitor_button = tb.Button(button_frame, text="Stop", command=self.controller.stop_monitor, width=30)
        stop_monitor_button.pack(side="top", pady=5)

        logger.info("ControlFrame widgets created.")

    def update_status(self, status: str) -> None:
        self._status.set(status)
