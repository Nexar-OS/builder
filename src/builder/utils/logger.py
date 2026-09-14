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
        # Ensure parent dir exists
        log_file.parent.mkdir(exist_ok=True, parents=True)

        # Ensure log file will be new
        if log_file.is_file():
            log_file.unlink(missing_ok=True)

        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(logging.Formatter(format))

        logger.addHandler(file_handler)
    
    return logger

def create_default_logger(logfile: Path | None) -> None:
    """Create the default logger instance.

    Args:
        logfile (Path): The path to the log file.
    """

    global global_logger

    global_logger = create(
        name="builder",
        use_std_out=True,
        log_file=logfile.resolve() if logfile else None
    )

global_logger = None

def invoke(function, *args, **kwargs):
    if not global_logger:
        print("Global logger not initialized!")

    getattr(global_logger, function)(*args, **kwargs)

def warn(*args, **kwargs):
    invoke("warning", *args, **kwargs)

def info(*args, **kwargs):
    invoke("info", *args, **kwargs)

def debug(*args, **kwargs):
    invoke("debug", *args, **kwargs)

def exception(*args, **kwargs):
    invoke("exception", *args, **kwargs)

def error(*args, **kwargs):
    invoke("error", *args, **kwargs)