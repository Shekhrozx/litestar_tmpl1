import multiprocessing
import platform

from app import cli, core, db, domain

__all__ = ("cli", "core", "db", "domain")

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork", force=True)
