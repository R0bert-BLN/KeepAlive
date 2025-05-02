from src.gui.app import App
from loguru import logger

if __name__ == "__main__":
    try:
        logger.info("Starting application...")

        app = App()
        app.mainloop()

    except Exception as e:
        logger.error(f"Failed to start application: {e}")

    finally:
        logger.info("Application closed")
