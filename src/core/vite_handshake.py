import os
import time
import socket
import logging
from src.core.paths import get_bundle_dir

log = logging.getLogger("CodeMerger")

def _wait_for_listener(port, timeout=2.0):
    """Checks if a local port is actually accepting connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=0.1):
                return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.1)
    return False

def get_dev_url():
    """
    Reads the port from the .vite-port handshake file written by the Vite plugin.
    Ensures the backend connects to the correct frontend instance.
    """
    port_file = os.path.join(get_bundle_dir(), 'frontend', '.vite-port')

    # CRITICAL: Purge stale port file from previous sessions to avoid reading old data
    if os.path.exists(port_file):
        try:
            os.remove(port_file)
        except OSError:
            pass

    log.info("Dev Mode: Waiting for Vite port handshake...")

    # Wait up to 5 seconds for Vite to initialize and write the port file
    for _ in range(25):
        if os.path.exists(port_file):
            try:
                with open(port_file, 'r') as f:
                    port_str = f.read().strip()
                    if port_str:
                        port = int(port_str)
                        # Verification: Ensure Vite is actually listening
                        if _wait_for_listener(port):
                            log.info(f"Vite handshake received. Using port {port}")
                            return f"http://localhost:{port}"
            except (ValueError, Exception):
                pass
        time.sleep(0.2)

    log.warning("Vite handshake timed out. Falling back to default port 5173.")
    return "http://localhost:5173"