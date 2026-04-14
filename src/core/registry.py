import winreg
import sys
from ..core.paths import REGISTRY_KEY_PATH

def get_setting(name, default_value):
    """
    Reads a setting value, checking the user's preferences (HKCU) first,
    then falling back to the system-wide default (HKLM)
    """
    if sys.platform != "win32":
        return default_value

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return value
    except FileNotFoundError:
        pass
    except Exception:
        pass

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, name)
            if reg_type == winreg.REG_DWORD:
                return bool(value)
            return value
    except FileNotFoundError:
        return default_value
    except Exception:
        return default_value

def save_setting(name, value):
    """
    Saves a setting to the current user's personal registry key (HKCU)
    This allows user preferences to override system-wide defaults
    """
    if sys.platform != "win32":
        return

    try:
        # Always write to HKEY_CURRENT_USER to store the user's choice
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY_PATH) as key:
            if isinstance(value, bool):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, 1 if value else 0)
            elif isinstance(value, str):
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            elif isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
    except Exception:
        pass