"""
Personal Agent - Phase 1 Desktop Application Entry Point
"""
import sys
import os
import logging
from pathlib import Path

# Ensure project root directory is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "personal_agent.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("PersonalAgent")


def setup_environment() -> None:
    """Configure system and Qt runtime parameters."""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main():
    logger.info("Initializing Personal Agent Phase 1...")
    setup_environment()

    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from app.ui.main_window import MainWindow

        # Initialize Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName("Personal Agent")
        app.setOrganizationName("PersonalAgent")
        app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

        # Launch Main Window
        window = MainWindow()
        window.show()
        logger.info("Personal Agent main window launched successfully.")

        sys.exit(app.exec())

    except Exception as exc:
        logger.exception("Critical error during application startup: %s", exc)
        print(f"Startup Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
