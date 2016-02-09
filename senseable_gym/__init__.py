import logging

logger = logging.getLogger('senseable_logger')
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '| %(name)-12s | %(levelname)-8s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)
