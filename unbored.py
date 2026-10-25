"""The Unbored Button - a cute pink-themed boredom-busting desktop app.

Main entrypoint for running the application. Re-exports Application, DataManager,
and configuration constants for modularity and backwards compatibility.
"""
import config
from data_manager import BoredomDataManager, DataManager
from views import Application, MascotCanvas

__all__ = ["Application", "MascotCanvas", "DataManager", "BoredomDataManager", "config"]


def main():
    """Starts the application with High-DPI awareness enabled."""
    config.enable_high_dpi_awareness()
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
