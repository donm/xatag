import warnings

def xatag_formatwarning(msg, *a):
    # ignore everything except the message
    return str(msg) + '\n'

warnings.formatwarning = xatag_formatwarning

def warn(message):
    warnings.warn(message)
