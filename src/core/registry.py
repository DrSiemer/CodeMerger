import winreg
import sys
from ..core.paths import REGISTRY_KEY_PATH

def get_setting(name, default_value):
    """
    Reads a setting value, checking the user's preferences (HKCU) first,
    then falling back to the system-wide default (HKLM).
    """
    if sys.platform != "win32":
        return default_value # Registry is a Windows-only feature

    # 1. Try to read the user-specific setting from HKEY_CURRENT_USER
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return value
    except FileNotFoundError:
        # User-specific key or value doesn't exist, so fall back to system-wide.
        pass
    except Exception:
        # A different error occurred, fall back.
        pass

    # 2. Fallback: Try to read the system-wide default from HKEY_LOCAL_MACHINE
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return value
    except FileNotFoundError:
        # No system-wide default found either.
        return default_value
    except Exception:
        return default_value

def save_setting(name, value):
    """
    Saves a setting to the current user's personal registry key (HKCU).
    This allows user preferences to override system-wide defaults.
    """
    if sys.platform != "win32":
        return # Cannot save to registry on non-Windows platforms

    try:
        # Always write to HKEY_CURRENT_USER to store the user's choice.
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH) as key:
            if isinstance(value, bool):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, 1 if value else 0)
            elif isinstance(value, str):
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            elif isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
    except Exception:
        # Silently fail if registry writing is not possible.
        pass