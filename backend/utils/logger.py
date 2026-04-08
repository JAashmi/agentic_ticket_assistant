import logging
import os


LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def get_logger(name="app_logger"):
    """
    Configure and return logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:

        # 🔹 File handler
        file_handler = logging.FileHandler(f"{LOG_DIR}/app.log")
        file_handler.setLevel(logging.INFO)

        # 🔹 Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 🔹 Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger