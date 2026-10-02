class PMOError(Exception):
    """Base error for Personal Memory OS."""


class ValidationError(PMOError):
    """Raised when user-controlled data is invalid."""


class DriftError(PMOError):
    """Raised when a system-owned file was modified outside the updater."""
