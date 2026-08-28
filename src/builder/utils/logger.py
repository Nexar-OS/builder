import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("builder")

warn      = logger.warning
info      = logger.info
debug     = logger.debug
critical  = logger.critical
exception = logger.exception
error     = logger.error