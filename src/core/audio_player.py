from loguru import logger
import pygame
from pathlib import Path

class AudioPlayer:
    _is_mixer_init = False

    @staticmethod
    def init_mixer() -> None:
        if not AudioPlayer._is_mixer_init:
            try:
                pygame.mixer.init()
                AudioPlayer._is_mixer_init = True

                logger.info("Mixer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize mixer: {e}")

    @staticmethod
    def quit_mixer() -> None:
        if AudioPlayer._is_mixer_init:
            try:
                if pygame.mixer.get_busy():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()

                pygame.mixer.quit()
                AudioPlayer._is_mixer_init = False

                logger.info("Mixer quit successfully")
            except Exception as e:
                logger.error(f"Failed to quit mixer: {e}")

    @staticmethod
    def play_audio(file_path: str, volume: float) -> None:
        if not Path(file_path).exists():
            logger.error(f"Audio file not found: {file_path}")
            return

        if not AudioPlayer._is_mixer_init:
            AudioPlayer.init_mixer()

        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()

            logger.info(f"Playing audio: {file_path}")
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
