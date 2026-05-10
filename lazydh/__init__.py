from importlib.metadata import version

from . import reader, statblocks, utils

__all__ = ["reader", "statblocks", "utils"]
__author__ = "Dakota Y. Hawkins"
__version__ = version("lazydh")
