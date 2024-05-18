import logging.config


def setup_logging(log_file: str) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger('FolderSynchronizer')
    logger.setLevel(logging.INFO)

    # Create file handler which logs all messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)

    # Create console handler which logs INFO and higher level messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger