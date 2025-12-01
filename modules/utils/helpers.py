import importlib.util
import psutil

def check_psutil():
    """
    Check if psutil is installed and importable.
    """
    try:
        import psutil
        return True
    except ImportError:
        return False


def check_matplotlib():
    """
    Check if matplotlib is installed and importable.
    """
    spec = importlib.util.find_spec("matplotlib")
    return spec is not None


def get_psutil():
    return psutil
