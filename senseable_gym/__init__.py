#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

# Senseable Gym Logging Configuration

# This is the name that all other loggers must have as their root
global_logger_name = 'senseable_logger'

# Create the base logger
logger = logging.getLogger(global_logger_name)

# {{{ Handlers
handler = logging.StreamHandler()

# }}}
# {{{ Formatters
formatter = logging.Formatter(
        '| %(name)-12s | %(levelname)-8s | %(message)s')

# }}}
# {{{ Attach Handlers and Formatters
handler.setFormatter(formatter)
logger.addHandler(handler)
# }}}
# {{{ Level Management
logger.setLevel(logging.ERROR)

EXTRA_DEBUG = 5
# }}}
