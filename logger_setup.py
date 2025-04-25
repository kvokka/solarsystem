# logger_setup.py
import logging
import config

def setup_logger():
    """Configures and returns the logger."""
    logging.basicConfig(
        filename=config.LOG_FILE,
        filemode='w',  # Overwrite log file each run
        level=logging.INFO,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    # Optional: Add a handler to also print logs to console
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # formatter = logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)
    # console_handler.setFormatter(formatter)
    # logging.getLogger().addHandler(console_handler)

    return logging.getLogger("SimulationLogger")

logger = setup_logger()
