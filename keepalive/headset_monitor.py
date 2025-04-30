import sounddevice as sd
import threading
import time
import os
from .audio_player import play_sound


class HeadsetMonitor:
    def __init__(self, status_callback = None, settings_callback = None):
        self._thread = None
        self._stop = threading.Event()
        self._status_callback = status_callback
        self._settings_callback = settings_callback
        self._current_settings = {}
    
    def _update_status(self, message):
        if self._status_callback:
            self._status_callback(message)
        
        print(f"INFO: {message}")
    
    def _get_settings(self):
        if self._settings_callback:
            return self._settings_callback()
        
        return {}
    
    def _get_output_devices(self):
        try:
            devices = sd.query_devices()
            output_devices = []
            
            for device in devices:
                if device["max_output_channels"] > 0:
                    output_devices.append(device["name"].lower())
            
            return output_devices
        except Exception as e:
            self._update_status(f"Error getting output devices: {e}")
            print(f"ERROR: Error getting output devices: {e}")
            
            return []
    
    def _is_headset_connected(self, target_headsets):
        if not target_headsets:
            return False
        
        connected_devices = self._get_output_devices()
        
        for target_headset in target_headsets:
            for connected_device in connected_devices:
                if target_headset in connected_device:
                    print(f"INFO: Headset {target_headset} connected")
                    return True
        
        return False

    def _monitor_loop(self):
        self._update_status("Monitoring headset")
        
        while not self._stop.is_set():
            try:
                self._current_settings = self._get_settings()
                target_headsets = self._current_settings.get("target_headsets", [])
                sound_file = self._current_settings.get("sound_file", None)
                volume = self._current_settings.get("volume", 0.5)
                interval_minutes = self._current_settings.get("interval_minutes", 5)
                interval_seconds = interval_minutes * 60
                
                if not target_headsets:
                    self._update_status("No target headsets configured")
                    
                    if self._stop.wait(30):
                        break
                    
                    continue
                    
                if not sound_file or not os.path.exists(sound_file):
                    self._update_status("No sound file configured")
                    
                    if self._stop.wait(30):
                        break
                    
                    continue
                
                if self._is_headset_connected(target_headsets):
                    self._update_status("Headset connected")
                    play_sound(sound_file, volume)
                    
                    if self._stop.wait(interval_seconds):
                        break
                else:
                    if self._stop.wait(30):
                        break
            except Exception as e:
                self._update_status(f"Error monitoring headset: {e}")
                print(f"ERROR: Error monitoring headset: {e}")
                
                if self._stop.wait(30):
                    break
                
        self._update_status("Monitoring headset stopped")
        self._thread = None
                
    def start(self):
        if self.is_running():
            self._status_callback("Headset monitor already running")
            return False
        
        settings = self._get_settings()
        
        if not settings:
            self._status_callback("No settings found")
            return False
        
        if not settings.get("target_headsets"):
            self._status_callback("No target headsets configured")
            return False
        
        if not settings.get("sound_file"):
            self._status_callback("No sound file configured")
            return False
        
        self._stop.clear()
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.start()
        
        self._update_status("Headset monitor started")
        return True
    
    def stop(self):
        if not self.is_running():
            self._status_callback("Headset monitor not running")
            return 
        
        self._stop.set()
        print("INFO: Headset monitor stopped")
    
    def join(self, timeout = 2.0):
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout)
            
            if self._thread.is_alive():
                print("INFO: Headset monitor thread did not stop in time")
            else:
                self._thread = None
                print("INFO: Headset monitor thread stopped")
    
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()
