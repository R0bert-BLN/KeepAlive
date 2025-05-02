import ttkbootstrap as tb
import tkinter as tk
from loguru import logger
from ttkbootstrap.dialogs import Messagebox

class HeadsetFrame(tb.Frame):
    def __init__(self, parent: tb.Frame, controller) -> None:
        super().__init__(parent, padding=10, borderwidth=1, relief="solid")
        self.add_headset_combobox = tb.Combobox()
        self.headset_listbox = tk.Listbox
        self.controller = controller
        self.create_widgets()

    def create_widgets(self) -> None:
        list_frame = tb.Frame(self)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.headset_listbox = tk.Listbox(list_frame, height=5, selectmode=tk.SINGLE, relief="flat", borderwidth=1)
        self.headset_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=self.headset_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.headset_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = tb.Frame(self)
        button_frame.pack(side="right", fill="y", padx=(5, 0))

        self.add_headset_combobox = tb.Combobox(button_frame, values=[], width=40, state="readonly")
        self.add_headset_combobox.set("Select device to add...")
        self.add_headset_combobox.pack(fill="x", pady=2)

        add_headset_button = tb.Button(button_frame, text="Add", command=self._add_headset, width=8)
        add_headset_button.pack(fill="x", pady=2)

        remove_headset_button = tb.Button(button_frame, text="Remove", command=self._remove_headset, width=8)
        remove_headset_button.pack(fill="x", pady=2)

        logger.info("HeadsetFrame widgets created.")

    def _add_headset(self) -> None:
        headset_name = self.add_headset_combobox.get().strip().lower()

        if not headset_name or headset_name == "select device to add...":
            Messagebox.show_warning(message="Please select a device to add", title="Warning", parent=self)
            return

        self.controller.request_add_headset(headset_name)
        self.add_headset_combobox.set("Select device to add...")
        logger.info("Headset added successfully")

    def _remove_headset(self) -> None:
        selected_indices = self.headset_listbox.curselection()

        if not selected_indices:
            Messagebox.show_warning(message="Please select a device to remove", title="Warning", parent=self)
            return

        selected_index = selected_indices[0]
        headset_name = self.headset_listbox.get(selected_index)
        self.controller.request_remove_headset(headset_name)
        logger.info("Headset removed successfully")

    def update_list(self, devices: list) -> None:
        self.headset_listbox.delete(0, tk.END)

        for name in devices:
            self.headset_listbox.insert(tk.END, name)

        logger.info("Headset list updated successfully")

    def update_available_devices(self, devices: list) -> None:
        self.add_headset_combobox.config(values=devices)
        logger.info("Available devices updated successfully")
