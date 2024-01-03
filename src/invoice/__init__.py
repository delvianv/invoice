# __init__.py
# Copyright (c) 2024  Delvian Valentine <delvian.valentine@gmail.com>

__author__ = "Delvian Valentine <delvian.valentine@gmail.com>"
__version__ = "1.1"

from importlib import resources

import invoice

DATA = resources.files(invoice) / "data"


def version():
    return __version__
