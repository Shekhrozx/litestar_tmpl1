from importlib.metadata import PackageNotFoundError, metadata, version

__all__ = ("__project__", "__version__")


try:
    __version__ = version("litestar-init")
    """Version of the project."""

    __project__ = metadata("litestar-init")["Name"]
    """Name of the project."""
except PackageNotFoundError:
    __version__ = "0.0.1"
    """Version of the project."""
    __project__ = "litestar-init"
    """Name of the project."""
finally:
    del version, PackageNotFoundError, metadata