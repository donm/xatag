import warnings

def xatag_formatwarning(msg, *a):
    """Ignore everything except the message."""
    return str(msg) + '\n'

warnings.formatwarning = xatag_formatwarning

def warn(message):
    """Print a warning to stderr."""
    warnings.warn(message)

