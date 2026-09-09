import logging
from pathlib import Path

FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

def create(
    name: str,
    use_std_out: bool = True,
    log_file: Path | None = None,
    format: str | None = None
) -> logging.Logger:
    """
    Create a logger instance.

    Args:
        name (str): The name of the logger
        use_std_out (bool, optional): If set to `False`` no output will be printed to stdout. Defaults to True.
        log_file (Path | None, optional): An optional file to dump the logs in to. Defaults to None.
        format (str | None, optional): Override the default logger format from ``builder.logger.FORMAT``.

    Returns:
        logging.Logger: The logger instance.
    """
    format = format or FORMAT

    logger = logging.Logger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    if use_std_out:
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(logging.Formatter(format))

        logger.addHandler(stdout_handler)
    
    if log_file:
        # Ensure log file will be new
        if log_file.is_file():
            log_file.unlink(missing_ok=True)

        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(logging.Formatter(format))

        logger.addHandler(file_handler)
    
    return logger


# Global logger
global_logger = create(
    name="builder",
    use_std_out=True,
    log_file=Path("builder.log").resolve()
)

warn      = global_logger.warning
info      = global_logger.info
debug     = global_logger.debug
critical  = global_logger.critical
exception = global_logger.exception
error     = global_logger.error