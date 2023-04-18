import logging
import os


def setup_logging():
    TESTING = (
        True if os.path.basename(os.getcwd()) == "PhilippinesAuditSystem" else False
    )
    if TESTING:
        log_file_path = "test_log.txt"
    else:
        log_file_path = "../data/log.txt"
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
