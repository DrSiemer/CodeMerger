import socket
import json
import uuid
import time
import logging
import threading

log = logging.getLogger("CodeMerger")

class UnrealClient:
    """
    A lightweight client for Unreal Engine's Python Remote Execution.
    Implements discovery via multicast and command execution via TCP.
    """
    def __init__(self):
        self.connected = False
        self.command_socket = None
        self.remote_node_id = None
        self.remote_address = None
        
        # Configuration
        self.multicast_group = ('239.0.0.1', 6766)
        self.local_node_id = str(uuid.uuid4())
        self.timeout = 2.0

    def connect(self, timeout=2.0):
        """
        Attempts to discover an Unreal Editor instance and connect to it.
        Returns True if successful.
        """
        self.disconnect()
        self.timeout = timeout
        
        log.info("Attempting to discover Unreal Engine...")
        
        # 1. Discovery via Multicast
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Send a discovery ping
            msg = {
                "type": "ping",
                "source": self.local_node_id,
                "version": 1
            }
            sock.sendto(json.dumps(msg).encode('utf-8'), self.multicast_group)
            
            # Listen for 'pong' response
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = sock.recvfrom(4096)
                    resp = json.loads(data.decode('utf-8'))
                    if resp.get('type') == 'pong':
                        self.remote_node_id = resp.get('source')
                        cmd_endpoint = resp.get('command_endpoint')
                        if cmd_endpoint:
                            ip, port = cmd_endpoint.split(':')
                            self.remote_address = (ip, int(port))
                            log.info(f"Found Unreal Engine at {self.remote_address}")
                            break
                except socket.timeout:
                    break
                except Exception:
                    continue
            sock.close()
            
            if not self.remote_address:
                log.info("Unreal Engine discovery timed out.")
                return False

            # 2. Connect via TCP
            self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.command_socket.settimeout(5.0) # Longer timeout for execution
            self.command_socket.connect(self.remote_address)
            self.connected = True
            log.info("Connected to Unreal Engine command socket.")
            return True

        except Exception as e:
            log.error(f"Unreal connection failed: {e}")
            self.disconnect()
            return False

    def disconnect(self):
        if self.command_socket:
            try:
                self.command_socket.close()
            except Exception:
                pass
        self.command_socket = None
        self.connected = False
        self.remote_address = None

    def is_connected(self):
        return self.connected

    def run_script(self, script_content):
        """
        Sends a python script string to Unreal and returns the stdout output.
        """
        if not self.connected or not self.command_socket:
            return None

        try:
            # Prepare command message
            msg = {
                "type": "command",
                "source": self.local_node_id,
                "target": self.remote_node_id,
                "command": script_content,
                "unattended": True
            }
            
            # Send
            data = json.dumps(msg).encode('utf-8')
            self.command_socket.sendall(data)
            
            # Receive response (accumulate chunks)
            buffer = b""
            while True:
                chunk = self.command_socket.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                try:
                    # Try to decode what we have so far
                    decoded = buffer.decode('utf-8')
                    if decoded.strip().endswith('}'):
                        json.loads(decoded)
                        break
                except Exception:
                    continue
            
            response = json.loads(buffer.decode('utf-8'))
            if response.get('type') == 'command_result':
                return response.get('output')
            
            return None

        except Exception as e:
            log.error(f"Error running script in Unreal: {e}")
            self.disconnect() # Assume connection died
            return None