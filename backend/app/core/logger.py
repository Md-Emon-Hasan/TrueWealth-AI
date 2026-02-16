import logging
import os


def setup_logger(name="backend"):
    # Define logs directory inside backend folder
    # BASE_DIR is backend/app/core, so backend is 2 levels up
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_root = os.path.dirname(os.path.dirname(current_dir))
    logs_dir = os.path.join(backend_root, "logs")

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, f"{name}.log")

    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if the logger is already configured
    if not logger.handlers:
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file)
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)

        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(log_format)
        f_handler.setFormatter(log_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger


# Initialize default logger
logger = setup_logger()
