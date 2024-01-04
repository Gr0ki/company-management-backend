"""Contains project's loggers."""

import logging


def get_logger(module_name: str):
    logger = logging.getLogger(module_name)
    return logger
